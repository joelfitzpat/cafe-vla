"""
frame_debug_node.py
Subscribes to /cafe/camera/image_raw and saves every Nth frame as a PNG
into /ros2_ws/debug_frames/ (which is mounted from the Windows host).

Open the debug_frames/ folder in File Explorer on Windows to inspect
what the VLA camera is actually seeing.

Usage (inside container):
    source /opt/ros/jazzy/setup.bash
    python3 /ros2_ws/src/frame_debug_node.py
"""

import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

SAVE_DIR    = '/ros2_ws/debug_frames'
SAVE_EVERY  = 10   # save one frame out of every N received


class FrameDebugNode(Node):
    def __init__(self):
        super().__init__('frame_debug_node')
        self._bridge = CvBridge()
        self._count  = 0
        os.makedirs(SAVE_DIR, exist_ok=True)

        self.create_subscription(
            Image, '/cafe/camera/image_raw', self._image_callback, 10
        )
        self.get_logger().info(
            f'Frame debug node ready — saving every {SAVE_EVERY}th frame to {SAVE_DIR}/'
        )

    def _image_callback(self, msg: Image):
        self._count += 1
        if self._count % SAVE_EVERY != 0:
            return

        bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        path = os.path.join(SAVE_DIR, f'frame_{self._count:06d}.png')
        cv2.imwrite(path, bgr)
        self.get_logger().info(f'Saved {path}')


def main(args=None):
    rclpy.init(args=args)
    node = FrameDebugNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
