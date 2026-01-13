# Installation

## Install with pip

PySFCGAL is now accessible on the [Python Package Index (PyPI)](https://pypi.org/project/PySFCGAL/). You can install it in a Python virtual environment. For example, on Debian or Ubuntu systems, you might use the following steps:

- Create and activate a virtual environment
- Use pip to install PySFCGAL from PyPI

```bash
python -m .venv
source .venv/bin/activate
pip install pysfcgal
```

## Install from scratch

### Build dependencies

The dependencies required for the build are:

- gmp
- boost
- mpfr
- cmake
- cgal*

Install SFCGAL with your package manager (apt, yum, pacman, pkg, etc) or with the sources if your system doesn't offer the package.

Example for debian/ubuntu users:

```shell
apt install -y cmake libgmp-dev libmpfr-dev libboost-dev libboost-timer-dev libboost-test-dev
```

### CGAL

Only required if your distribution does not provide the updated package (version `5.6` or later), otherwise you can direclty install `CGAL` from your package manager.

For debian/ubuntu

```shell
apt install libcgal-dev
```

Manual installation

```shell
wget "https://github.com/CGAL/cgal/releases/download/v6.1/CGAL-6.1.tar.xz" -O CGAL-6.1.tar.xz
tar xJf CGAL-6.1.tar.xz
```

Remember your path to CGAL - we'll need it later. Example: `/home/foo/CGAL-6.1`.

### SFCGAL

Clone [SFCGAL](https://gitlab.com/sfcgal/SFCGAL) and place yourself in the `SFCGAL` folder:

```shell
git clone git@gitlab.com:sfcgal/SFCGAL.git && cd SFCGAL
```

Then build SFCGAL considering the path to CGAL:

```shell
cmake -GNinja -S . -B build -DSFCGAL_BUILD_TESTS=ON -DCGAL_DIR=/home/foo/CGAL-6.1
cmake --build build
```

The build includes can be found here: `/home/foo/SFCGAL/build/src`

You may optionally install SFCGAL to your system through:

```shell
cmake --install build
```

### PySFCGAL

#### Build the python module

To start you have to clone [pysfcgal](https://gitlab.com/sfcgal/pysfcgal) and place yourself in the `pysfcgal` folder:

```shell
git clone git@gitlab.com:sfcgal/pysfcgal.git && cd pysfcgal
```

Then install the Python binding through:

```shell
env CFLAGS=-I/home/foo/SFCGAL/build/include LDFLAGS=-L/home/foo/SFCGAL/build/src python3 -m build
python3 -m pip install --user
```

Where:

- `LDFLAGS` is the path where to find `libSFCGAL.so`
- `CFLAGS` is the path where the build includes are located

#### Add the build source link of SFCGAL into the ld file (on Debian/Ubuntu)

The Pysfcgal installation ends with the modification of your `LD_LIBRARY_PATH` variable:

```shell
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/foo/SFCGAL/build/src
```

Alternatively, you may create a ldconfig file as follows:

```shell
echo "/home/foo/SFCGAL/build/src" >> /etc/ld.so.conf.d/sfcgal.conf
```

and run this command to apply the changes:

```shell
sudo ldconfig
```

## How to build the documentation?

Project uses [MkDocs](https://www.mkdocs.org/) to generate documentation with themes [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). Pages are written in Markdown.

### Install requirements

```bash
python -m pip install -U -r requirements/documentation.txt
```

### Build documentation website

To build it:

```bash
cd docs && mkdocs build --verbose --strict
```

Then open `docs/site/index.html` in a web browser.

## Write documentation using live render

```bash
cd docs && mkdocs serve
```

Open <http://localhost:8000> in a web browser to see the HTML render updated when a file is saved.
