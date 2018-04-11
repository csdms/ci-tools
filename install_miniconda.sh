#! /bin/bash

MINICONDA_URL_BASE="https://repo.continuum.io/miniconda/Miniconda3-latest"

if [[ "$(uname)" == "Darwin" ]]; then
  OS="MacOSX-x86_64"
else
  OS="Linux-x86_64"
fi

miniconda_sh=$(mktemp)

curl $MINICONDA_URL_BASE-$OS.sh > $miniconda_sh
bash $miniconda_sh $*
conda config --set always_yes yes --set changeps1 no
