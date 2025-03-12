class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool_name, tool_function):
        self.tools[tool_name] = tool_function

    def get_tool(self, tool_name):
        return self.tools.get(tool_name, None)
