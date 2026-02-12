title: AI IT Project Delivery Assistant
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
license: mit
python_version: 3.10

# HuggingFace Spaces Configuration
# This file configures your Space for deployment

# App Configuration
app_file: backend/main.py
models: []
datasets: []
pinned: false
tags:
  - ai
  - it-project
  - project-management
  - fastapi
  - groq

# Hardware Configuration
hardware: cpu-basic
runtime: docker

# Environment Variables (set in HuggingFace UI)
# GROQ_API_KEY: your_groq_api_key_here
