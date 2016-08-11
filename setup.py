"""Setup script"""

from setuptools import setup
BUILD = "3"
VERSION = "1.0." + BUILD

setup(
    name                = 'bg_deploy',
    version             = VERSION,
    description         = 'Blue Green Deployment Script',
    url                 = 'https://github.com/jwplayer/operations/bg_deploy',
    author              = 'JWPlayer DevOps Team',
    author_email        = 'team@jwplayer.com',
    maintainer          = 'Louis DeLosSantos',
    maintainer_email    = 'louis@jwplayer.com',
    scripts             = [
        'scripts/bg_deploy'
    ],
    packages            = ['bg_deploy', 'bg_deploy.AWS_Models', 'bg_deploy.States'],
    package_dir         = {'bg_deploy': 'bg_deploy'},
    install_requires    = [
        'boto3',
    ],
)
