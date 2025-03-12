# Manus Open

## Multi-Agent Framework

Manus Open is designed with a multi-agent architecture to handle various tasks efficiently. The architecture is composed of the following key components:

### Core Agents
- **Coordinator Agent**: Manages the overall workflow and coordinates between different agents.
- **Planner Agent**: Plans and schedules tasks based on the input requests.
- **Knowledge Agent**: Manages and retrieves knowledge from various sources.
- **Executor Agent**: Executes the planned tasks and integrates with external tools.

### Tool Integration
- **Tool Registry**: Manages and registers various tools for automation.
- **Browser Automation**: Automates browser actions.
- **Data Processing**: Processes and analyzes data.
- **API Connectors**: Connects to external APIs.
- **Deployment Systems**: Manages deployment of models and applications.

### Memory Systems
- **Episodic Memory**: Stores session-specific information.
- **Semantic Memory**: Stores and queries semantic knowledge.
- **Procedural Memory**: Records workflows and procedures.

### Model Router
- **Model Router**: Routes tasks to the appropriate Large Language Models (LLMs) based on the task type.
- **Primary LLM**: Handles planning tasks.
- **Secondary LLM**: Handles domain-specific tasks.
- **Task-Specific Models**: Handles specialized tasks.

## Configuration
The LiteLLM model is configured using environment variables for the API key and model name. The configuration is managed in the `config.py` file.

## Getting Started
To get started with Manus Open, follow these steps:

1. **Install Dependencies**: Ensure all necessary dependencies are installed.
2. **Set Environment Variables**: Set the `LLM_API_KEY` and `LLM_MODEL` environment variables.
3. **Run the Application**: Execute the `main.py` file to start the multi-agent framework.

```bash
python main.py
```

## Contributing
Contributions are welcome! Please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
