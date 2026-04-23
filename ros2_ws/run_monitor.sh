#!/bin/bash
# Terminal C — watch action vectors being published to /cafe/action
source /opt/ros/humble/setup.bash
ros2 topic echo /cafe/action
