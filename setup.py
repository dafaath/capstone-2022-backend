import os

from setuptools import find_packages, setup

filename = "requirements.txt"
full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
with open(full_path_filename) as f:
    requirements = f.read().splitlines()

setup(
    name='emodiary',
    version='0.0.1',
    packages=find_packages(exclude=['app/tests']),  # Include all the python modules except `tests`.
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python',
    ],
)
