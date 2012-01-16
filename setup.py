from setuptools import setup, find_packages


VERSION = (0, 3)
version = '.'.join(map(str, VERSION))

setup(
    name='jscc',
    version=version,
    author='Pavel Reznikov',
    author_email='pashka.reznikov@gmail.com',
    description='jscc is a tool that helps you compile js code using google clusure compiler.',
    url='https://github.com/troolee/jscc',

    install_requires=[
        'setuptools',
        'PyYAML'
    ],

    entry_points={
        'console_scripts': [
            'jscc = jscc:main'
        ]
    },

    packages=find_packages(),
)
