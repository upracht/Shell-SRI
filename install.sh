#!/bin/bash

cp lite_LT.py lite_LT
chmod +x lite_LT
echo "export PYTHONPATH=\$PYTHONPATH:$PWD" >> ~/.bashrc
echo "export PATH=\$PATH:$PWD" >> ~/.bashrc
