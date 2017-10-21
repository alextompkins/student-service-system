from setuptools import setup

setup(
    name='serviceapp',
    packages=['serviceapp'],
    include_package_data=True,
    install_requires=[
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf'
    ],
)