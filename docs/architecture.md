# **Architecture Overview**

This demo is organized into **four** parts:

## 1. AI model module 
- It provides a clean intergace for AI inference.
- In the public version, it is stubbed to avoid shipping any model weights or device-specific setup.

## 2. MCP module
- Represents the orchestration layer.
- In a real setup, this would manage tool calls and the flow between user prompts, model inference and integration.

## 3. Integrations
- External system integrations are mocked.
- This keeps the repository privacy-safe and avoids exposing any real Git service configuration.

## 4. Entry point 
- It demonstrates the workflow end-to-end using the modules above.