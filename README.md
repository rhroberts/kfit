[![kfit](https://snapcraft.io/kfit/badge.svg)](https://snapcraft.io/kfit)

<div align="center">
<a href="./images/kfit_v2.svg">
    <img src="./images/kfit_v2.svg" width="10%" />
</a>
<h1>kfit - Simple, graphical spectral fitting</h1>
</div>
<div>
kfit is a tool for quick and easy spectral fitting in science and education.
It works as a standalone data fitting program for simple tasks, or as an
exploratory tool in more complex projects. kfit provides a few commonly 
used peak shapes in engineering and physics, and will eventually support 
custom models.
<br><br>
</div>
<div align="center">
<img src="./assets/screenshot.png" />
</div>

## Installation (Linux)

### From snapcraft

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/kfit)

```bash
sudo snap install kfit
```

Instructions for installing `snapd` for each compatible linux distro:

[https://snapcraft.io/docs/installing-snapd](https://snapcraft.io/docs/installing-snapd)

Snap has been tested on:

- Ubuntu 18.04 and 19.04 :heavy_check_mark:

- Debian 10 :heavy_check_mark:

- Red Hat Enterprise Linux 7 :heavy_check_mark:

- Fedora 30*

- OpenSUSE Tumbleweed*

*See [https://github.com/rhroberts/kfit/issues/2](https://github.com/rhroberts/kfit/issues/2)

### From source

Install:

```bash
sudo apt install python3 python3-pip python3-gi python3-gi-cairo
git clone git@github.com:rhroberts/kfit.git
cd kfit
pip3 install ./
```

Run:

```bash
./kfit/kfit.py
```

#### Dependencies

Python packages

- lmfit
- matplotlib
- pandas
- numpy

Distro packages

- python3
- python3-pip
- python3-gi
- python3-gi-cairo

## Installation (Windows)

*STILL WORKING ON THIS*

I've tested the following with Windows 10 and Anaconda's python3 distribution. After installing conda and opening up a conda prompt:

1. Create a conda env
   
   . `conda create -n kfit python=3.7`
   
   . `conda activate kfit`

2. Install dependencies
   
   - `conda install numpy matplotlib pandas pycairo`
   . `conda install -c conda-forge pygobject`
   
   . `pip install lmfit`

3. Download and unzip kfit source code
   
   . https://github.com/rhroberts/kfit/archive/master.zip

4. Navigate to the project root

5. Run `python kfit/kfit.py`

*Currently, this produces the following error:*

> Traceback (most recent call last):
>   File "C:\Users\rhrob\Anaconda3\envs\kfit\lib\site-packages\matplotlib\backends\backend_gtk3.py", line 25, in <module>
>     gi.require_version("Gtk", "3.0")
>   File "C:\Users\rhrob\Anaconda3\envs\kfit\lib\site-packages\gi\__init__.py", line 129, in require_version
>     raise ValueError('Namespace %s not available' % namespace)
> ValueError: Namespace Gtk not available
> 
> The above exception was the direct cause of the following exception:
> 
> Traceback (most recent call last):
>   File "kfit.py", line 7, in <module>
>     from matplotlib.backends.backend_gtk3cairo import (
>   File "C:\Users\rhrob\Anaconda3\envs\kfit\lib\site-packages\matplotlib\backends\backend_gtk3cairo.py", line 1, in <module>
>     from . import backend_cairo, backend_gtk3
>   File "C:\Users\rhrob\Anaconda3\envs\kfit\lib\site-packages\matplotlib\backends\backend_gtk3.py", line 29, in <module>
>     raise ImportError from e
> ImportError

## Contributing

- Check out [NOTES.md](./NOTES.md) for development notes and TODOs
