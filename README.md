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

- [https://snapcraft.io/docs/installing-snapd](https://snapcraft.io/docs/installing-snapd)

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

[https://github.com/rhroberts/kfit/issues/3](https://github.com/rhroberts/kfit/issues/3)

## Contributing

- Check out [NOTES.md](./NOTES.md) for development notes and TODOs
