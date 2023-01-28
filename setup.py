from distutils.util import convert_path
from setuptools import find_packages, setup

module_name = "py7dtd"
main_ns = {}
ver_path = convert_path(f"src/{module_name}/version.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name=module_name,
    version=main_ns["__version__"],
    packages=find_packages(where="src", exclude=["tests*"]),
    package_dir={"": "src"},
    license="MIT",
    description="Collection of 7 Days to Die bots, scripts and hacks",
    keywords=["7dtd", "bots", "hacks", "scripts"],
    long_description_content_type="text/markdown",
    long_description=open("README.md", encoding="utf8").read(),
    install_requires=[
        "swig==4.1.1",
        "pywin32==305",
        "pyWinhook==1.6.2",
        "pillow==9.4.0",
        "pyperclip==1.8.2",
    ],
    url="https://github.com/tassoneroberto/py7dtd",
    author="Roberto Tassone",
    author_email="roberto.tassone@proton.me",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "py7dtd_model_training = py7dtd.ai.training:main",
            "py7dtd_crack_passcode = py7dtd.bots.crack_passcode:main",
            "py7dtd_auto_shooting = py7dtd.bots.auto_shooting:main",
            "py7dtd_blocks_detection = py7dtd.scripts.blocks_detection:main",
        ],
    },
)
