[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/Thanaraklee/Head-Require/blob/main/LICENSE)
[![Upload Python Package](https://github.com/Thanaraklee/Head-Require/actions/workflows/python-publish.yml/badge.svg?event=release)](https://github.com/Thanaraklee/Head-Require/actions/workflows/python-publish.yml)

![head-require](https://github.com/Thanaraklee/Head-Require/blob/main/img/logo.jpg)

# Head-Require

Head-Require is a Python library designed to simplify the process of generating `requirements.txt` files based on the imported packages in Python files within your project.

## How to Use

### Installation

To install Head-Require, you can use pip:

```bash
pip install head-require
```

### Usage

Once installed, you can use the `head-require` command in the current directory of your project. Here are some common usage examples:

To generate the `requirements.txt` file based on the imported packages in your Python files, simply run:

```bash
head-require
```

#### Help

For a list of available options and their descriptions, you can use the help option:

```bash
head-require -h
```

### Additional Notes

- Make sure to run the `head-require` command in the root directory of your Python project.
- Head-Require analyzes Python files (`*.py` and `*.ipynb`) to extract imported packages and their versions.

❗**Important:**
This command must be executed within the `activated environment`. If it's not activated, it will work under the machine's environment.

Thank you for using Head-Require! 😊
