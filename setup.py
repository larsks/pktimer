from setuptools import setup, find_packages
import sys

if sys.version_info.major < 3:
    raise ValueError('This package requires Python 3 or later')

setup(
    name='pktimer',
    version='0.1',
    description='A simple interval timer',
    url='https://github.com/larsks/pktimer',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    license='GPL',
    keywords='interval timer pecha-kucha',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pktimer=pktimer.main:main',
        ],
    },
)
