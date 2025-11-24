#!/bin/bash

echo "Initializing Ollama models..."

# Pull lightweight models for CPU
docker exec ollama ollama pull phi3

# List available models
echo "Available models:"
docker exec ollama ollama list

echo "Ollama is ready! Access at http://localhost:11434"