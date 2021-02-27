# py7dtd - A 7 Days to Die tools collection

![detection](preview/logo.png)

<https://7daystodie.com/>

In this repository are collected tools and scripts for the game 7 Days to Die:

- Tools for the detection of objects/entities
- Scripts for the automatization of actions (mining, crafting, etc.)
- Aim bots
- Passcode cracking

## Installation

Disclaimer: an NVIDIA® GPU card with CUDA® architectures 3.5, 3.7, 5.2, 6.0, 6.1, 7.0 or higher is required. See the list of CUDA®-enabled GPU cards (<https://developer.nvidia.com/cuda-gpus>).

### Windows

Install the following dependencies:

- C++ redistributable (<https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads>)
- NVIDIA® GPU drivers —CUDA® 11.2.1 (<https://www.nvidia.com/drivers>)
- CUDA® Toolkit 11.1 (<https://developer.nvidia.com/cuda-toolkit-archive>)
- cuDNN SDK 7.6 (<https://developer.nvidia.com/cudnn>)

(More info here: <https://www.tensorflow.org/install/gpu>)

In order to use the module you need a `x64` version of `Python 3.7.x`.
You can download it at this page: <https://www.python.org/downloads/windows/>

Download link: <https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe>

Clone the module, create a virtual environment and install it:

```bash
git clone git@github.com:tassoneroberto/py7dtd.git
cd py7dtd
py -3.7 -m venv venv
.\venv\Scripts\Activate.ps1
py -3.7 -m pip install .
```

## Entities detection

❗ Under development ❗

Simple entities detector using AI (Computer Vision).

The objects detection (trees, zombies, etc.) is done using `ImageAI`: <https://github.com/OlafenwaMoses/ImageAI/>

The annotation of the images has been done using the tool `labelImg`: <https://github.com/tzutalin/labelImg>

### Proof of concept

![detection](preview/preview1.png)

## Aim bot

❗ Under development ❗

Simple aim bot capable of:

- Detect zombies/players
- Move the mouse to the target
- Shoot

### Usage

```bash
py7dtd_auto_shooting
```

![detection](preview/preview2.png)

## Passcode cracking

❗ Under development ❗

Bruteforce/dictionary attack on chests/doors passcode.

### Usage

Example of a bruteforce attack testing passcodes of 2-10 characters length, with a delay of 20ms between each try and a limit of 100 tries.

```bash
py7dtd_crack_passcode --brute --min 2 --max 10 --delay 20 --limit 100
```

![detection](preview/bruteforce-preview.gif)

Example of a dictionary attack with a delay of 30ms between each try and no limit in tries.

```bash
py7dtd_crack_passcode --dict --dictpath passwords.txt --delay 30
```

Note: dictionaries can be found at <https://github.com/danielmiessler/SecLists/tree/master/Passwords>.

![detection](preview/dictionary-preview.gif)

### Command line arguments

The available methods are **bruteforce attack** (`--brute`) and **dictionary attack** (`--dict`).

The following table is listing all the arguments to use for each method:

| arg           |  description      |  default  | type     |
|:-------------:|:-----------------:| :--------:|:--------:|
| min           | Minimum length                | `1`|`brute`|
| max           | Maximum length                | `20`|`brute`|
| dictpath      | Dictionary file path          | `None`|`dict`*|
| limit         | Maximum number of tries       | `∞`|`brute`, `dict`|
| delay         | Delay in ms between each mouse/keyboard action  | `20`|`brute`, `dict`|

**this attribute is required*
