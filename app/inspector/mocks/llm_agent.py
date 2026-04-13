class Agent:
    def __init__(self, model=None, name=None, description=None, instruction=None, tools=None, sub_agents=None, **kwargs):
        self.model = model
        self.name = name
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        print(f"[MOCK] Initialized Agent: {self.name} (Tools: {len(self.tools)})")


        