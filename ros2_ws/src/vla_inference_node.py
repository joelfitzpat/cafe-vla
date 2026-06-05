"""
vla_inference_node.py
Subscribes to two fixed external cameras (/entrance_camera/image_raw and
/far_camera/image_raw) and runs OpenVLA-OFT inference, publishing action
chunks to /cafe/action.

The entrance camera (Camera 1) triggers inference. The far camera (Camera 2)
provides a complementary view — when the robot moves toward one camera it
moves away from the other, minimising occlusion of the action space.

Model loads in a background thread at startup — expect ~1-2 min before
the node is ready. CPU inference takes 30-120s per frame; frames are
skipped while inference is in progress.
"""

import json
import threading
import numpy as np
import sys
import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

sys.path.insert(0, '/opt/openvla-oft')
from experiments.robot.openvla_utils import (
    get_action_head,
    get_processor,
    get_proprio_projector,
    get_vla,
    get_vla_action,
)
from prismatic.vla.constants import NUM_ACTIONS_CHUNK, PROPRIO_DIM

# Minimal re-implementation of GenerateConfig so we don't need the LIBERO
# simulation package (libero) that run_libero_eval.py depends on.
from dataclasses import dataclass, field
from typing import Optional, Union
from pathlib import Path

@dataclass
class GenerateConfig:
    pretrained_checkpoint: Union[str, Path] = ""
    model_family: str = "openvla"
    use_l1_regression: bool = True
    use_diffusion: bool = False
    num_diffusion_steps_train: int = 50
    num_diffusion_steps_inference: int = 50
    use_film: bool = False
    num_images_in_input: int = 2
    use_proprio: bool = True
    center_crop: bool = True
    num_open_loop_steps: int = 8
    lora_rank: int = 32
    unnorm_key: Union[str, Path] = ""
    load_in_8bit: bool = False
    load_in_4bit: bool = False
    run_id_note: Optional[str] = None
    local_log_dir: str = "./experiments/logs"
    use_wandb: bool = False
    wandb_entity: str = ""
    wandb_project: str = ""
    seed: int = 7

PRETRAINED_CHECKPOINT = "moojink/openvla-7b-oft-finetuned-libero-spatial"
TASK_DESCRIPTION = "Navigate to the counter."


class VLAInferenceNode(Node):
    def __init__(self):
        super().__init__('vla_inference_node')

        # Camera 1 (entrance) — triggers inference on each frame.
        self.create_subscription(
            Image, '/entrance_camera/image_raw', self._entrance_callback, 10
        )
        # Camera 2 (far end) — latest frame is stored and used as the
        # second input slot when Camera 1 triggers inference.
        self.create_subscription(
            Image, '/far_camera/image_raw', self._far_callback, 10
        )
        self.publisher_ = self.create_publisher(String, '/cafe/action', 10)

        self._model_ready = False
        self._busy = False
        self._lock = threading.Lock()
        self._bridge = CvBridge()
        self._frame_count = 0
        self._latest_far_frame: Image = None  # updated by _far_callback
        self._logged_loading_warn = False

        self.get_logger().info('Loading OpenVLA-OFT model in background — this takes 1-2 min on CPU...')
        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self):
        # accelerate's dispatch_model tries to call .to() after bitsandbytes has
        # already placed the quantized model on the correct device, which raises
        # a ValueError. Patch the reference inside transformers.modeling_utils
        # (where the call originates) to catch that specific error and return the
        # model as-is — it's already on the right device.
        import transformers.modeling_utils as _mu
        _orig_dispatch = _mu.dispatch_model
        def _safe_dispatch(model, *args, **kwargs):
            try:
                return _orig_dispatch(model, *args, **kwargs)
            except ValueError as e:
                if '.to' in str(e) and 'bitsandbytes' in str(e):
                    return model
                raise
        _mu.dispatch_model = _safe_dispatch

        cfg = GenerateConfig(
            pretrained_checkpoint=PRETRAINED_CHECKPOINT,
            use_l1_regression=True,
            use_diffusion=False,
            use_film=False,
            num_images_in_input=2,
            use_proprio=True,
            load_in_8bit=False,
            load_in_4bit=True,
            center_crop=True,
            num_open_loop_steps=NUM_ACTIONS_CHUNK,
            unnorm_key="libero_spatial_no_noops",
        )
        self._cfg = cfg
        self._vla = get_vla(cfg)
        self._processor = get_processor(cfg)
        self._action_head = get_action_head(cfg, llm_dim=self._vla.llm_dim)
        self._proprio_projector = get_proprio_projector(
            cfg, llm_dim=self._vla.llm_dim, proprio_dim=PROPRIO_DIM
        )
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # action_head and proprio_projector are plain nn.Modules — they load
        # to CPU by default and must be moved to match the quantised VLA weights.
        if device == 'cuda':
            self._action_head = self._action_head.to(device)
            self._proprio_projector = self._proprio_projector.to(device)
            # 4-bit quantised loading places parameters on CUDA but leaves some
            # registered buffers (e.g. rotary embedding inv_freq) on CPU.
            # Move every buffer that ended up on the wrong device.
            for module in self._vla.modules():
                for buf_name in list(module._buffers.keys()):
                    buf = module._buffers[buf_name]
                    if buf is not None and buf.device.type == 'cpu':
                        module._buffers[buf_name] = buf.to(device)
        self._model_ready = True
        self.get_logger().info(
            f'Model ready — running on {device.upper()}. '
            'Listening on /entrance_camera/image_raw and /far_camera/image_raw.'
        )

    def _far_callback(self, msg: Image):
        # Just store the latest frame — no inference triggered here.
        self._latest_far_frame = msg

    def _entrance_callback(self, msg: Image):
        if not self._model_ready:
            if not self._logged_loading_warn:
                self.get_logger().warn('Model still loading — frames will be skipped until ready.')
                self._logged_loading_warn = True
            return

        with self._lock:
            if self._busy:
                self.get_logger().warn('Inference in progress, skipping frame.')
                return
            self._busy = True

        threading.Thread(target=self._run_inference, args=(msg,), daemon=True).start()

    def _decode_image(self, msg: Image) -> np.ndarray:
        """Convert a ROS Image message to a (224, 224, 3) uint8 RGB array."""
        bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if rgb.shape[:2] != (224, 224):
            rgb = cv2.resize(rgb, (224, 224))
        return rgb.astype(np.uint8)

    def _run_inference(self, entrance_msg: Image):
        try:
            full_image = self._decode_image(entrance_msg)

            # Use the latest far camera frame if available, otherwise fall back
            # to the entrance view so inference is never blocked by a missing frame.
            far_msg = self._latest_far_frame
            wrist_image = self._decode_image(far_msg) if far_msg is not None else full_image.copy()

            observation = {
                'full_image': full_image,
                'wrist_image': wrist_image,
                'state': np.zeros(PROPRIO_DIM, dtype=np.float64),
                'task_description': TASK_DESCRIPTION,
            }

            self._frame_count += 1
            frame_id = self._frame_count
            self.get_logger().info(f'Running inference on frame #{frame_id}...')

            actions = get_vla_action(
                self._cfg,
                self._vla,
                self._processor,
                observation,
                TASK_DESCRIPTION,
                self._action_head,
                self._proprio_projector,
            )

            for step, action in enumerate(actions):
                action_msg = String()
                action_msg.data = json.dumps({
                    'frame_id': frame_id,
                    'step': step,
                    'action': action.tolist(),
                    'device': 'cpu',
                    'instruction': TASK_DESCRIPTION,
                })
                self.publisher_.publish(action_msg)

            self.get_logger().info(
                f'Frame #{frame_id}: published {len(actions)} action steps.'
            )
        except Exception as e:
            import traceback
            self.get_logger().error(f'Inference error: {e}\n{traceback.format_exc()}')
        finally:
            with self._lock:
                self._busy = False


def main(args=None):
    rclpy.init(args=args)
    node = VLAInferenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
