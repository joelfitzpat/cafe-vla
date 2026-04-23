#!/bin/bash
# Terminal A — publishes randomised fake camera frames to /cafe/camera
source /opt/ros/humble/setup.bash
python3 /ros2_ws/src/camera_stub_rand_node.py
