from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-objcounter",
    version="0.1.0",
    description="CLI harness for YOLO Object Counter (object detection and counting service)",
    author="YOLO Object Counter Team",
    python_requires=">=3.10",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "PyYAML>=6.0",
        "ultralytics>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-objcounter=cli_anything.objcounter.objcounter_cli:main",
            "count=cli_anything.objcounter.objcounter_cli:main",
            "counton=cli_anything.objcounter.lifecycle:counton",
            "countoff=cli_anything.objcounter.lifecycle:countoff",
            "countkey=cli_anything.objcounter.lifecycle:countkey",
        ],
    },
)
