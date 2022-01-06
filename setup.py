from distutils.core import setup

setup(
    name='sts-creds',
    version='0.1.0',
    author='WeGift',
    scripts=['bin/sts-creds.py'],
    license='LICENSE.txt',
    description='Wrapper that provides deployment credentials using STS',
    install_requires=[
        "boto3 >= 1.17.97"
    ],
)
