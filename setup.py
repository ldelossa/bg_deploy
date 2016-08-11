"""Setup script"""

from setuptools import setup
BUILD = "3"
VERSION = "1.0." + BUILD

setup(
    name                = 'bg_deploy',
    version             = VERSION,
    description         = 'Blue Green Deployment Script',
    scripts             = [
        'scripts/bg_deploy'
    ],
    packages            = ['bg_deploy', 'bg_deploy.AWS_Models', 'bg_deploy.States'],
    package_dir         = {'bg_deploy': 'bg_deploy'},
    install_requires    = [
        'boto3',
    ],
)
