class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, tool):
        self.tools[name] = tool

    def get_tool(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.keys())
