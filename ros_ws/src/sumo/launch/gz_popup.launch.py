from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.conditions import IfCondition

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare, FindPackagePrefix
from launch.substitutions import PathJoinSubstitution, Command, LaunchConfiguration

import yaml



def generate_launch_description():
    share_dir = PathJoinSubstitution([
        FindPackagePrefix("sumo"),
        "share",
    ])

    env = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=share_dir
    )

    xacro_file = PathJoinSubstitution([
        FindPackageShare("sumo"),
        "urdf",
        "sumo.xacro"
    ])

    robot_description = {
        "robot_description": Command(["xacro ", xacro_file])
    }

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            ])
        ),
        launch_arguments={
            "gz_args": "-r empty.sdf"
        }.items()
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description]
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", "sumo"
        ]
    )

    config_file = PathJoinSubstitution([
                    FindPackageShare("sumo"),
                    "config",
                    "bridge_parameters.yaml"
                ])

    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            'config_file': config_file
        }]
    )

    
    # rviz = LaunchConfiguration('rviz')
    # rviz2 = GroupAction(
    #     condition=IfCondition(rviz),
    #     actions=[Node(
    #                 package='rviz2',
    #                 executable='rviz2',
    #                 output='screen',)]
    # )

    return LaunchDescription([
        env,
        gazebo,
        robot_state_publisher,
        spawn_robot,
        ros_gz_bridge
    ])