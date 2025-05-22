#!/bin/sh

set -e

pip install twine

mkdir dist
cp -r dist_windows/* dist/
cp -r dist_linux_*/* dist/
