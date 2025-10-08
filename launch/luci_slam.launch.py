import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, LogInfo, RegisterEventHandler
from launch.conditions import IfCondition
from launch.substitutions import AndSubstitution, LaunchConfiguration, NotSubstitution
from launch_ros.actions import Node, LifecycleNode
from launch_ros.events.lifecycle import ChangeState
from launch_ros.event_handlers import OnStateTransition
from lifecycle_msgs.msg import Transition
from launch.events import matches_action


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    use_lifecycle_manager = LaunchConfiguration('use_lifecycle_manager')

    # # Default params file path (update path as needed)
    # default_slam_params_path = os.path.join(
    #     get_package_share_directory('luci-ros2-slam'), 'config', 'slam_params.yaml'
    # )
    # slam_params_file = LaunchConfiguration('slam_params_file', default=default_slam_params_path)

    # PointCloud2LaserScan node
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='cloud_to_scan',
        output='screen',
        parameters=[{
            'target_frame': 'base_link',
            'transform_tolerance': 0.01,
            'min_height': 0.0,
            'max_height': 1.0,
            'angle_min': -3.14,
            'angle_max': 3.14,
            'angle_increment': 0.01,
            'scan_time': 0.1,
            'range_min': 0.2,
            'range_max': 5.0,
            'use_inf': True,
            'use_sim_time': use_sim_time,
        }],
        remappings=[
            ('cloud_in', '/luci/camera_points'),
            ('scan', '/scan')
        ]
    )
    
    # EKF Localization Node (robot_localization)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[{
            'frequency': 50.0,
            'sensor_timeout': 0.1,
            'two_d_mode': True,
            'odom0': '/odom',   # raw encoder odometry
            'odom0_config': [True, True, False,
                             False, False, True,
                             True, False, False,
                             False, False, False,
                             False, False, False],
            'imu0': '/luci/imu',
            'imu0_config': [False, False, False,
                            False, False, True,   # yaw orientation
                            False, False, False,
                            False, False, True,   # yaw velocity
                            False, False, False],
            'world_frame': 'odom',
            'odom_frame': 'odom',
            'base_link_frame': 'base_link'
        }]
    )

    # SLAM Toolbox Lifecycle node
    slam_toolbox_node = LifecycleNode(
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox',
        namespace='',  
        output='screen',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'odom_frame': 'odom',
                'map_frame': 'map',
                'base_frame': 'base_link',
                'scan_topic': 'scan',
                'mode': 'mapping',
                'use_lifecycle_manager': use_lifecycle_manager,
                'odom_topic': '/odometry/filtered',   # use EKF output
                'max_laser_range': 5.0,
                'use_loop_closure': True,
                'loop_search_maximum_distance': 5.0,
                'loop_closure_search_radius': 5.0,    # small hallways
                'loop_closure_match_threshold': 0.55   # more permissive
            }
        ],
    )

    # Emit configure lifecycle event if autostart and no lifecycle manager
    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam_toolbox_node),
            transition_id=Transition.TRANSITION_CONFIGURE
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager)))
    )

    # Register handler to activate after configured
    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_toolbox_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                LogInfo(msg="[LifecycleLaunch] SLAM Toolbox node is activating."),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(slam_toolbox_node),
                        transition_id=Transition.TRANSITION_ACTIVATE
                    )
                )
            ]
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager)))
    )

    ld = LaunchDescription()

    # Declare launch arguments with defaults
    ld.add_action(DeclareLaunchArgument('use_sim_time', default_value='false',
                                       description='Use simulation time'))
    ld.add_action(DeclareLaunchArgument('autostart', default_value='true',
                                       description='Automatically start SLAM Toolbox node'))
    ld.add_action(DeclareLaunchArgument('use_lifecycle_manager', default_value='false',
                                       description='Use lifecycle manager'))
    # ld.add_action(DeclareLaunchArgument('slam_params_file',
    #                                    default_value=default_slam_params_path,
    #                                    description='Full path to SLAM Toolbox params file'))

    # Add nodes and lifecycle event handlers
    ld.add_action(pointcloud_to_laserscan_node)
    ld.add_action(ekf_node)
    ld.add_action(slam_toolbox_node)
    ld.add_action(configure_event)
    ld.add_action(activate_event)

    return ld
