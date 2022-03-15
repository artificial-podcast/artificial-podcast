from setuptools import find_packages
from setuptools import setup

# keep this in sync with requirements.txt

REQUIRED_PACKAGES = ['aitextgen', 'google-cloud-storage']

setup(
    name='trainer',
    version='1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='AI generated fanfiction'
)