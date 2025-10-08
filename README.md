# luci-ros2-slam

This package provides SLAM (Simultaneous Localization and Mapping) functionality for the LUCI robot using ROS 2.

## Dependencies

- ROS 2 (Humble or newer)
- `luci_bringup` package
- SLAM toolbox (`slam_toolbox`)
- EKF localization (`robot_localization`)

Install dependencies:
```bash
sudo apt update
sudo apt install ros-<ros2-distro>-slam-toolbox ros-<ros2-distro>-robot-localization
```
Replace `<ros2-distro>` with your ROS 2 distribution (e.g., `humble`).

## Usage

1. **Source your ROS 2 workspace:**
    ```bash
    source /opt/ros/<ros2-distro>/setup.bash
    source ~/ros2_ws/install/setup.bash
    ```

2. **Launch LUCI bringup:**
    ```bash
    ros2 launch luci_bringup bringup.launch.py
    ```

3. **Launch SLAM:**
    ```bash
    ros2 launch luci_ros2_slam luci_slam.launch.py
    ```

## Notes

- Ensure all required sensors are connected and configured.
- Adjust parameters in `luci_slam.launch.py` as needed for your environment.

## Troubleshooting

- Check ROS 2 nodes with `ros2 node list`.
- View SLAM and localization topics with `ros2 topic list`.
- Inspect logs for errors.

## License

See [LICENSE](LICENSE) for details.