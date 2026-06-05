#!/bin/bash
# Launch Gazebo with the real cafe world and spawn the Krytn robot.
# Make sure you have run build.sh first.
source /opt/ros/jazzy/setup.bash
source /ros2_ws/install/setup.bash
ros2 launch krytn gazebo.launch.py
