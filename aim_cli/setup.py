from setuptools import setup, find_packages

setup(
    name='aim-cli',
    version='3.0.0',
    description='AIM v3 Command-Line Interface',
    author='AIM Team',
    packages=find_packages(where='.'),
    py_modules=['aim', 'trainer'],
    entry_points={
        'console_scripts': [
            'aim=aim:cli',
        ],
    },
    install_requires=[
        'click>=8.0.0',
        'requests>=2.25.0',
    ],
    python_requires='>=3.8',
)
