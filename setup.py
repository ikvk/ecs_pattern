import os
import re
import setuptools


def get_version(package: str) -> str:
    """Return package version as listed in __version__ variable at __init__.py"""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", init_py).group(1)


with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ecs-pattern',
    version=get_version('ecs_pattern'),
    packages=setuptools.find_packages(exclude=['tests']),
    url='https://github.com/ikvk/ecs_pattern',
    license='Apache-2.0',
    license_files="LICENSE",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Vladimir Kaukin',
    author_email='KaukinVK@ya.ru',
    description='Implementation of the ECS pattern for creating games',
    keywords=['python3', 'python', 'ecs', 'pattern', 'architecture', 'games', 'gamedev'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
