from glob import glob

from setuptools import find_packages, setup

package_name = 'so101_perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='CSCI 4551 project team',
    maintainer_email='maintainers@example.com',
    description='Camera-based perception (OpenCV + cv_bridge) for the SO-101.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'vision_node = so101_perception.vision_node:main',
        ],
    },
)
