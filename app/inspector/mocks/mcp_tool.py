class McpToolset:
    def __init__(self, connection_params=None, tool_names=None):
        self.connection_params = connection_params
        self.tool_names = tool_names or []

class StdioConnectionParams:
    def __init__(self, command=None, args=None, env=None):
        self.command = command
        self.args = args or []
        self.env = env or {}