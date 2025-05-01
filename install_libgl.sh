#!/bin/sh
set -e

# Install libGL.so.1 at runtime
apt-get update && apt-get install -y libgl1 && apt-get clean
