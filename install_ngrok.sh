#!/bin/bash

# Script to install and configure ngrok

# Check if ngrok is already installed
if command -v ngrok &> /dev/null; then
    echo "Ngrok is already installed."
else
    echo "Installing ngrok..."

    # Check if Arch Linux or Debian-based
    if command -v pacman &> /dev/null; then
        # Arch Linux - download binary
        echo "Downloading ngrok for Linux..."
        curl -o ngrok-v3-stable-linux-amd64.tgz https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
        sudo tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin
        rm ngrok-v3-stable-linux-amd64.tgz
    elif command -v apt &> /dev/null; then
        # Debian/Ubuntu
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
        echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
        sudo apt update && sudo apt install ngrok
    else
        echo "Unsupported package manager. Please install ngrok manually from https://ngrok.com/download"
        exit 1
    fi
    echo "Ngrok installed."
fi

# Configure auth token
echo "Enter your ngrok authtoken (get from https://dashboard.ngrok.com):"
read -s token
if [ -n "$token" ]; then
    ngrok config add-authtoken "$token"
    echo "Token configured."
else
    echo "No token provided. Run 'ngrok config add-authtoken YOUR_TOKEN' manually."
fi

echo "To expose ports, run: ngrok http 3000 & ngrok http 5000 &"