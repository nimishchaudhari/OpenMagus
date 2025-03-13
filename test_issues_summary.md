# Test Issues Summary

## Database Connection Issues

### Redis (localhost:6379)
- Connection refused errors affecting:
  - Agent integration tests
  - Episodic memory tests
- Solution: Need to start Redis server locally

### Neo4j (localhost:7687)
- Connection refused errors affecting:
  - Procedural memory tests
- Solution: Need to start Neo4j server locally

### ChromaDB
- Using deprecated configuration
- Solution: Update to new ChromaDB client configuration format

## Configuration Issues

### Model Router
- Missing required 'provider' parameter in ModelConfig initialization
- Affects all model routing tests
- Solution: Update ModelConfig to include provider parameter

### Config Agent
- Missing required 'agent_name' parameter in load_config()
- Solution: Update test to provide agent_name parameter

## Browser Automation Issues
- Timeout errors in browser tests
- Connection closed while reading from driver
- Solution: Ensure browser dependencies are installed and browser can be launched

## Next Steps

1. Install and start required services:
   ```bash
   # Redis
   sudo service redis-server start

   # Neo4j
   sudo service neo4j start
   ```

2. Update ChromaDB configuration in semantic_memory.py

3. Update model configuration to include provider:
   ```python
   model = ModelConfig(
       model_name=os.getenv("LLM_MODEL"),
       api_key=os.getenv("LLM_API_KEY"),
       provider="openrouter"  # Add this
   )
   ```

4. Update config agent test to include agent name

5. Verify browser automation dependencies:
   ```bash
   python -m playwright install
