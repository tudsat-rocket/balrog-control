# balrog-control
Balrog Testbench Control &amp; Telemetry Software

---

## Installation & Setup

The testbench builts upon the TinkerForge ecosystem of modules ([Go here for a primer](https://www.tinkerforge.com/en/doc/Primer.html)) and therefore some dependencies need to be installed. 

---

### Install brick daemon 

The brick daemon (brickd) provides the API-bindings for communicating with the TinkerForge modules. For installation instructions for various platforms refer to the brickd [GitHub page](https://github.com/Tinkerforge/brickd). 

---

### Create environment 

All python dependencies are maintained as a conda environment in a `environment.yaml` file. After installation of [Conda](https://conda.org/) or a comparable distribution (eg. [Mircomamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)), install with:

```
conda env create -f environment.yml
```

---

## Usage

--- 


