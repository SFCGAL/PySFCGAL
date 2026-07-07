#!/bin/sh

set -e

USAGE="Usage: $0 <python_version> [devel_version] [devel_date]"

PYTHON_VERSION="$1"
DEVEL_VERSION="$2"
DEVEL_DATE="$3"
SFCGAL_VERSION="$4"

if [ -z "$PYTHON_VERSION" ]; then
  echo "$USAGE"
  exit 1
fi

if [ "${DEVEL_VERSION}" = "true" ] && [ -z "${DEVEL_DATE}" ]; then
    echo "Error: devel_date must be provided when devel_version is true."
    echo "$USAGE"
    exit 1
fi

echo "Python version: ${PYTHON_VERSION}"
if [ "${DEVEL_VERSION}" = "true" ]; then
    echo "DEVEL VERSION is enabled"
    echo "DEVEL DATE: ${DEVEL_DATE}"
else
    echo "DEVEL VERSION is disabled"
fi

echo "SFCGAL VERSION: ${SFCGAL_VERSION}"

# Update package definitions
brew update

# install SFCGAL
curl -L -o sfcgal.rb "https://gitlab.com/api/v4/projects/19674165/packages/generic/homebrew/${SFCGAL_VERSION}/sfcgal-${SFCGAL_VERSION}.rb"
brew tap-new local/sfcgal
mv sfcgal.rb "$(brew --repo local/sfcgal)/Formula/sfcgal.rb"
brew install local/sfcgal/sfcgal

# check SFCGAL installation
test -f "$(brew --prefix)/lib/libSFCGAL.dylib"

# install python if necessary
brew install python@"${PYTHON_VERSION}"
PYTHON_EXEC="/opt/homebrew/bin/python${PYTHON_VERSION}"
if [ ! -x "$PYTHON_EXEC" ]; then
    echo "Python executable not found at ${PYTHON_EXEC}"
    exit 1
fi

# Increase the dev version number to upload the wheel to gitlab package registry
if [ "${DEVEL_VERSION}" = "true" ]; then
    ${PYTHON_EXEC} ./ci/increment_version.py ${DEVEL_DATE}
fi

# create venv and build pysfcgal
${PYTHON_EXEC} -m venv venv
. ./venv/bin/activate
python3 -m pip install -U pip build delocate twine
python3 -m build

# repair wheel to include external libs with delocate-wheel
WHEEL_DIR="dist_macos_${PYTHON_VERSION}"
delocate-wheel -w "${WHEEL_DIR}"  -v dist/*.whl

# check the wheel
twine check --strict "${WHEEL_DIR}"/*
