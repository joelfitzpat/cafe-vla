"""
vla_inference_node.py
Subscribes to /cafe/camera, runs real OpenVLA-OFT inference, publishes
action chunks to /cafe/action.

Model loads in a background thread at startup — expect ~1-2 min before
the node is ready. CPU inference takes 30-120s per frame; frames are
skipped while inference is in progress.
"""

import json
import os
import threading
import numpy as np
import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

sys.path.insert(0, os.environ.get('OPENVLA_PATH', '/opt/openvla-oft'))
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
TASK_DESCRIPTION = "Navigate to the delivery table without hitting obstacles."


class VLAInferenceNode(Node):
    def __init__(self):
        super().__init__('vla_inference_node')
        self.subscription = self.create_subscription(
            String, '/cafe/camera', self.camera_callback, 10
        )
        self.publisher_ = self.create_publisher(String, '/cafe/action', 10)

        self._model_ready = False
        self._busy = False
        self._lock = threading.Lock()

        self.get_logger().info('Loading OpenVLA-OFT model in background — this takes 1-2 min on CPU...')
        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self):
        cfg = GenerateConfig(
            pretrained_checkpoint=PRETRAINED_CHECKPOINT,
            use_l1_regression=True,
            use_diffusion=False,
            use_film=False,
            num_images_in_input=2,
            use_proprio=True,
            load_in_8bit=False,
            load_in_4bit=False,
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
        self._model_ready = True
        self.get_logger().info('Model ready — subscribed to /cafe/camera.')

    def camera_callback(self, msg: String):
        if not self._model_ready:
            self.get_logger().warn('Model still loading, skipping frame.')
            return

        with self._lock:
            if self._busy:
                self.get_logger().warn('Inference in progress, skipping frame.')
                return
            self._busy = True

        frame = json.loads(msg.data)
        threading.Thread(target=self._run_inference, args=(frame,), daemon=True).start()

    def _run_inference(self, frame):
        try:
            # Build (224, 224, 3) uint8 images from the stub's mean_rgb values.
            # When real cameras are wired in, replace these with decoded pixel data.
            mean_rgb = frame.get('mean_rgb', [0.5, 0.5, 0.5])
            rgb_uint8 = (np.clip(mean_rgb, 0.0, 1.0) * 255).astype(np.uint8)
            full_image = np.full((224, 224, 3), rgb_uint8, dtype=np.uint8)
            wrist_image = np.full((224, 224, 3), rgb_uint8, dtype=np.uint8)

            observation = {
                'full_image': full_image,
                'wrist_image': wrist_image,
                'state': np.zeros(PROPRIO_DIM, dtype=np.float64),
                'task_description': TASK_DESCRIPTION,
            }

            frame_id = frame.get('frame_id', '?')
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
            self.get_logger().error(f'Inference error: {e}')
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
