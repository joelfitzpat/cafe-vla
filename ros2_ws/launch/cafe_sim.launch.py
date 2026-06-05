"""
cafe_sim.launch.py
Starts headless Gazebo Harmonic (gz sim) with the café world and
bridges the camera gz topic to the ROS 2 topic that vla_inference_node
subscribes to.

Usage (inside container):
    source /opt/ros/jazzy/setup.bash
    ros2 launch /ros2_ws/launch/cafe_sim.launch.py
"""

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


WORLD_PATH = '/ros2_ws/worlds/cafe.world'


def generate_launch_description():
    # gz sim in server-only mode (-s) with headless EGL rendering.
    # LIBGL_ALWAYS_SOFTWARE=1 forces Mesa software renderer so the
    # camera sensor works on CPU-only / no-display machines.
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', '--headless-rendering', WORLD_PATH],
        output='screen',
        additional_env={'LIBGL_ALWAYS_SOFTWARE': '1'},
    )

    # ros_gz_bridge maps the Gazebo camera topic to the ROS 2 topic.
    # Format: <gz_topic>@<ros_msg>[<gz_msg>
    #   [ = unidirectional gz → ROS
    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='camera_bridge',
        arguments=[
            '/cafe/camera/image_raw'
            '@sensor_msgs/msg/Image'
            '[gz.msgs.Image',
        ],
        output='screen',
    )

    return LaunchDescription([
        gz_sim,
        camera_bridge,
    ])
