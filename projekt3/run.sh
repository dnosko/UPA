#!/bin/bash

PWD=`pwd`
VENV="venv"
PYTHON=$VENV/bin/python3
URLS="src.urls"
PRODUCTS="src.products"
tmpfile=$(mktemp)
output="$PWD/data_20.tsv"

. build.sh
echo $VIRTUAL_ENV
$PYTHON -m $URLS

echo `head -20 $PWD/urls.txt > $tmpfile`

$PYTHON -m $PRODUCTS $tmpfile $output
rm "$tmpfile"
