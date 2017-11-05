import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'qemu-affinity',
    version = '1.0.0',
    
    description = ('A tool to easily pin certain QEMU threads to select CPU cores.'),
    long_description=read('README.rst'),

    url = 'http://packages.python.org/an_example_pypi_project',

    author = 'Adam Zegelin',
    author_email = 'adam@zegelin.com',
    
    license = 'MIT',
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
    
    keywords = 'qemu affinity',
    
    py_modules=['qemu_affinity'],
    
    entry_points={
        'console_scripts': [
            'qemu-affinity=qemu_affinity:main',
        ],
    },
)
