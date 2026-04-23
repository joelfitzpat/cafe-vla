#!/bin/bash
# Terminal B — subscribes to /cafe/camera, runs stub VLA inference, publishes to /cafe/action
source /opt/ros/humble/setup.bash
python3 /ros2_ws/src/vla_inference_node.py
