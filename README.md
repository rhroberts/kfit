[![kfit](https://snapcraft.io/kfit/badge.svg)](https://snapcraft.io/kfit)

<div align="center">
<a href="./images/kfit_v2.svg">
    <img src="./images/kfit_v2.svg" width="10%" />
</a>
<h1>kfit - Simple, graphical spectral fitting</h1>
</div>
<div>
kfit is a tool for quick and easy spectral fitting in science and education. It works as a standalone data fitting program for simple tasks, or as an exploratory tool in more complex projects. kfit provides a few commonly used peak shapes in engineering and physics, and will eventually support custom, user-defined models.
<br><br>
</div>
<div align="center">
<img src="./assets/screenshot.png" />
</div>

## Usage

### Keyboard shortcuts

| Action                                | Shortcut       |
| ------------------------------------- |:--------------:|
| Fit                                   | `<Control>f`   |
| Reset                                 | `<Control>r`   |
| Import File                           | `<Control>o`   |
| Export Results                        | `<Control>s`   |
| Open Settings                         | `<Control>p`   |
| Add/Remove Gaussian To/From Model     | `g / <Shift>g` |
| Add/Remove Lorentzian To/From Model   | `l / <Shift>l` |
| Add/Remove Pseudo-Voigt To/From Model | `v / <Shift>v` |
| Add/Remove Line To/From Model         | `n / <Shift>n` |

### Importing Data

CSV files are imported via the [pandas.read_csv()](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html) method, and a few select parameters for this method can be accessed from the settings window in kfit. Generally, a comma-separated plaintext file with or without a header row and with UTF-8 encoding can be import with no issues. A more robust, interactive file import dialog will be implemented in a future release.

### Exporting Results

The export method will save two CSV files to the local filesystem:

1. ***.csv**
   
   The original data, total fit, and component curves in the fit.
   
   | x   | data | total_fit | [model_component_1] | ... | [model_component_N] |
   | --- |:----:|:---------:|:-------------------:|:---:|:-------------------:|
   | ... | ...  | ...       | ...                 | ... | ...                 |

2. ***.params.csv**
   
   The parameters for each model component, e.g. *gau1_amplitude*, *lin1_slope*, etc.
   
   | parameter                         | value |
   | --------------------------------- | ----- |
   | [model_component_1]_[parameter_1] |       |
   | [model_component_1]_[parameter_2] |       |
   | ...                               |       |
   | [model_component_N]_[parameter]_N |       |

### Models

At the moment, kfit uses four stock models from the [lmfit](https://lmfit.github.io/lmfit-py/) package: three peak-like models (Gaussian, Lorentzian, Pseudo-Voigt) and a Linear model. These base models can be added together to create a composite model for the data. In the future, support for more `lmfit` models and user-defined custom models will be added.

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
