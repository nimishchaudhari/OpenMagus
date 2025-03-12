class ExecutorAgent:
    def __init__(self, tool_registry, procedural_memory):
        self.tool_registry = tool_registry
        self.procedural_memory = procedural_memory

    def execute_plan(self, plan, session_id):
        # Execute each step in the plan
        for step in plan:
            tool = self.tool_registry.get_tool(step['tool'])
            result = tool.execute(step['params'])

            # Record the result in procedural memory
            self.procedural_memory.record_result(session_id, step, result)

        # Return the final result
        return result
