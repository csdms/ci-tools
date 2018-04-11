#! /bin/bash

prefix=$1

MINICONDA_URL_BASE="https://repo.continuum.io/miniconda/Miniconda3-latest"

if [[ "$(uname)" == "Darwin" ]]; then
  OS="MacOSX-x86_64"
else
  OS="Linux-x86_64"
fi

temp_dir=$(mktemp -d)

curl $MINICONDA_URL_BASE-$OS.sh > $temp_dir/miniconda.sh
bash $temp_dir/miniconda.sh -b -f -p $prefix
$prefix/bin/conda config --set always_yes yes --set changeps1 no
