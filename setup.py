from setuptools import setup, find_packages

setup(
    name='rsctl',
    version='0.2',
    description='Command-line control tool for RediSearch clusters',
    author='RedisLabs',
    url='https://github.com/redislabs/rsctl',
    scripts=['rsctl/rsctl'],
    license='BSD 2-clause',
    packages=find_packages(),
    install_requires=['redis', 'click', 'fabric', 'colorama']
)
