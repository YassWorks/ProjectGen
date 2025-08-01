# ProjectGen

ProjectGen is an AI-powered project generation system that uses multiple specialized agents to create complete software projects from natural language descriptions.

## Overview

The system employs a multi-agent architecture with three specialized agents:

- **BrainstormerAgent**: Analyzes project descriptions to extract core ideas, technical requirements, and feature suggestions
- **CodeGenAgent**: Generates complete project structures with code files, configurations, and documentation
- **WebSearcherAgent**: Searches for relevant information and best practices to enhance project generation

## Architecture

ProjectGen uses LangGraph for agent orchestration and Cerebras for language model inference. Each agent is equipped with specialized tools and system prompts tailored to their specific responsibilities.

The orchestration system coordinates between agents to transform initial project concepts into fully functional codebases with proper structure, dependencies, and documentation.

## Key Features

- Multi-agent collaborative approach to project generation
- Support for various programming languages and frameworks
- Automated project scaffolding and file generation
- Web research integration for up-to-date best practices
- Rich terminal interface with progress visualization

## Tutorial

Currently, the best way to test this project in a sandboxed environment is by launching a Docker container and then entering it via the terminal to experiment with the agent without any risks.

First, start the container:
```bash
docker compose up --build
```

Then enter the container:
```bash
docker exec -it projectgen-projectgen-1 /bin/sh
```

You may modify the `main.py` file as needed or run it directly:
```bash
python main.py
```
