#!/bin/bash

set -e

if [ ! -f requirements.txt ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

pip freeze > current.txt

grep -vxFf requirements.txt current.txt > to_remove.txt || true

if [ -s to_remove.txt ]; then
    echo "Uninstalling packages not listed in requirements.txt..."
    pip uninstall -y -r to_remove.txt
else
    echo "No extra packages to uninstall."
fi

rm -f current.txt to_remove.txt

echo "Cleanup complete."
