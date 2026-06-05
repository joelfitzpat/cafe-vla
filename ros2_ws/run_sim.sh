#!/bin/bash
# Terminal A — start headless Gazebo Harmonic with the café world.
# Camera publishes to /cafe/camera/image_raw once gz sim is running.
source /opt/ros/jazzy/setup.bash
ros2 launch /ros2_ws/launch/cafe_sim.launch.py
