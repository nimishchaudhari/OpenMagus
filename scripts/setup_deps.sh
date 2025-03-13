#!/bin/bash

# Update package lists
apt-get update

# Install build dependencies
apt-get install -y \
    build-essential \
    wget \
    zlib1g-dev

# Download and build SQLite 3.35.0
wget https://www.sqlite.org/2021/sqlite-autoconf-3350000.tar.gz
tar xvf sqlite-autoconf-3350000.tar.gz
cd sqlite-autoconf-3350000
./configure
make
make install
cd ..
rm -rf sqlite-autoconf-3350000*

# Update library links
ldconfig

# Install Python dependencies
pip install -r requirements.txt

# Set up test data directories
mkdir -p /tmp/chromadb
chmod 777 /tmp/chromadb
