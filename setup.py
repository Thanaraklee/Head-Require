from setuptools import setup, find_packages

classifiers = [
    "Programming Language :: Python :: 3",
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

setup(
    name='head_require',
    version='0.1.2',
    description='head-require is a library that aims to simplify the creation of requirements.txt files. head-require generates requirements.txt based on the packages actually used in your project.',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    author='Thanarak Leenanon',
    author_email='bzank.lee@hotmail.com',
    license='MIT',
    classifiers=classifiers,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'head-require = head_require.core:main',
        ],
    },
)
