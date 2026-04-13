class Part:
    def __init__(self, text=None, **kwargs):
        self.text = text

class Content:
    def __init__(self, role=None, parts=None, **kwargs):
        self.role = role
        self.parts = parts or []