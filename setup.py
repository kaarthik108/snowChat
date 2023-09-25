
from setuptools import setup, find_packages

setup(
    name='snowchat',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'streamlit',
    ],
    package_data={
        'snowchat': ['ui/*', 'docs/*', 'sql/*'],
    },
    entry_points={
        'console_scripts': [
            'snowchat=snowchat.cli:main',
        ],
    },
)
