#!/bin/bash

# Exit on error
set -e

echo "Installing browser dependencies..."

# Update package list
sudo apt-get update

# Install required packages
sudo apt-get install -y \
    libwoff2-1 \
    libopus0 \
    libwebpdemux2 \
    libharfbuzz-icu0 \
    libwebpmux3 \
    libenchant-2-2 \
    libhyphen0 \
    libegl1 \
    libglx0 \
    libgudev-1.0-0 \
    libevdev2 \
    libgles2 \
    x264

echo "Browser dependencies installed successfully!"
