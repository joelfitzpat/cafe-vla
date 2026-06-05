#!/bin/bash
# Build all ROS 2 packages in the workspace.
# Run this once after starting the container, and again whenever you change package files.
# Uses --merge-install so all packages share a single install/share/ directory,
# which is required for Gazebo to find models via GZ_SIM_RESOURCE_PATH.
source /opt/ros/jazzy/setup.bash
cd /ros2_ws
colcon build --merge-install --symlink-install
source /ros2_ws/install/setup.bash
echo "Build complete. Run run_krytn.sh to launch the simulation."
