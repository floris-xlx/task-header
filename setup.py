"""
Setup script for Linear Task Header application.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linear-task-header",
    version="1.0.0",
    author="Your Name",
    description="Always-on-top sticky GUI for Linear tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/linear-task-header",
    py_modules=[
        "main",
        "config",
        "linear_client",
        "sticky_header",
        "navigation_window",
        "markdown_sync"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.6.1",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "keyboard>=0.13.5",
        "watchdog>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "linear-task-header=main:main",
        ],
    },
)

