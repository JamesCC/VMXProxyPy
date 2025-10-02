# Use a Python 3.12 slim image instead of generic Ubuntu
FROM python:3.12-slim

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Since the official Python image is based on Debian/Buster,
# you might still need a few core development packages for pyserial
# if it has dependencies that require compilation.
# For pyserial, usually no extra packages are needed, but we can add
# the cleanup step.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install pyserial using pip (already configured)
RUN pip install pyserial
