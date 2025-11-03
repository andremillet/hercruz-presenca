#!/bin/bash

# Script to install and configure ngrok

echo "Installing ngrok..."

# Download and install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Note: User needs to set auth token manually: ngrok config add-authtoken <token>

echo "Ngrok installed. To configure, run: ngrok config add-authtoken YOUR_TOKEN"
echo "Then, to expose ports: ngrok http 3000 & ngrok http 5000 &"