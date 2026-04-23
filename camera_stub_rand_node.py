"""
camera_stub_rand_node.py
Like camera_stub_node but publishes randomised frame metadata so the
downstream vla_inference_node produces varied (non-zero) action vectors.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time
import random


class CameraStubRandNode(Node):
    def __init__(self):
        super().__init__('camera_stub_rand_node')
        self.publisher_ = self.create_publisher(String, '/cafe/camera', 10)
        self.timer = self.create_timer(1.0, self.publish_frame)
        self.frame_id = 0
        self.get_logger().info('Camera stub (random) node started — publishing to /cafe/camera')

    def publish_frame(self):
        self.frame_id += 1
        frame = {
            'frame_id': self.frame_id,
            'timestamp': time.time(),
            'width': 224,
            'height': 224,
            'channels': 3,
            'encoding': 'rgb8',
            'mean_rgb': [round(random.uniform(0.0, 1.0), 4) for _ in range(3)],
            'data': 'STUB — randomised frame metadata',
        }
        msg = String()
        msg.data = json.dumps(frame)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published random camera frame #{self.frame_id}')


def main(args=None):
    rclpy.init(args=args)
    node = CameraStubRandNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()