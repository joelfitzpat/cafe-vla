#!/bin/bash
# Terminal D — save camera frames as PNGs to ros2_ws/debug_frames/.
# Open that folder in Windows File Explorer to see what the camera sees.
source /opt/ros/jazzy/setup.bash
python3 /ros2_ws/src/frame_debug_node.py
