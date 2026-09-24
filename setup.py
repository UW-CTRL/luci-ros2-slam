from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'luci-ros2-slam'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kysh',
    maintainer_email='kmsw8001@uw.edu',
    description='SLAM integration for LUCI wheelchair',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['test_slam = luci_ros2_slam.wheelchair_camera_slam:main'],
    },
)
