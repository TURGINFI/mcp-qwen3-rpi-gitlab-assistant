# mcp-ai-workflow-integration-demo
Student demo: applied AI deployment &amp; MCP-based workflow integration (privacy-safe, mocked integrations)

# Applied AI System Integration Demo (Student Project)

This repository demonstrates a prototype of an applied AI system integrated into a development workflow using the Model Context Protocol (MCP).

The focus is **deployment and system integration** (applied AI engineering), not model training.

## Motivation

Modern AI systems create the most value when they are integrated into real workflows rather than used in isolation.
This demo was created as a learning exercise to understand production-oriented AI integration, orchestration, and workflow connections.

## What This Project Demonstrates

- MCP-based orchestration structure (simplified)
- A lightweight LLM inference interface (stubbed)
- Edge-friendly deployment mindset (in my original setup, I ran inference on Raspberry Pi using Qwen3 0.6B; **no training, inference only**)
- Integration with a Git service workflow (mocked here to avoid exposing any real systems)

## High-Level Architecture

User / Tool  
→ MCP Orchestrator  
→ AI Model Interface  
→ External System Integration (Mocked Git Service)

## Tech Stack (Demo)

- Python
- MCP (conceptual integration, simplified)
- Linux-friendly runtime
- Mocked Git service integration

## Project Structure

See `docs/architecture.md` for an overview.

## Running the Demo

1. Create a config file from the example:
   - Copy `config/config.example.yaml` to `config/config.yaml` (do **not** commit `config.yaml`)
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run:
   - `python -m src.main`

## Disclaimer (Privacy & Safety)

This is a student demo project created for learning purposes.
All external integrations are mocked, and **no real customer data, credentials, URLs, repositories, or production systems are included or exposed**.
