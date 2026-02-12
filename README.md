---
title: AI IT Project Delivery Assistant
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: "1.0.0"
python_version: "3.10"
app_file: backend/main.py
app_port: 7860
license: mit
pinned: false
models: []
datasets: []
tags:
  - ai
  - it-project
  - project-management
  - fastapi
  - groq
---

# AI IT Project Delivery Assistant

An intelligent AI-powered assistant for IT project delivery guidance using RAG (Retrieval-Augmented Generation) architecture.

## Features

- 🤖 **AI-Powered Guidance**: Uses Groq LLaMA3 for intelligent responses
- 📚 **Knowledge Base**: RAG architecture with FAISS vector store
- 🔧 **Tool Integration**: Risk scoring, timeline estimation, document generation
- 🎯 **Project Management**: Structured guidance for IT projects
- 🌐 **Modern UI**: Corporate-grade dashboard interface

## Deployment

This Space is deployed on HuggingFace Spaces using Docker.

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)

## Usage

1. Visit the deployed Space URL
2. Enter your IT project query
3. Get structured guidance with:
   - Overview
   - Planning
   - Execution
   - Risk Management
   - Deliverables
   - Success Metrics

## Technical Stack

- **Backend**: FastAPI with Python 3.10
- **AI**: Groq LLaMA3 + FAISS RAG
- **Frontend**: Modern JavaScript with responsive design
- **Deployment**: Docker on HuggingFace Spaces

## License

MIT License - see LICENSE file for details.

# Hardware Configuration
hardware: cpu-basic
runtime: docker

# Environment Variables (set in HuggingFace UI)
# GROQ_API_KEY: your_groq_api_key_here
