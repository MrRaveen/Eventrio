import importlib.abc
import importlib.util
import os

class Hook(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # Dynamically locate the 'mocks' directory next to this hook.py file
        base_dir = os.path.dirname(__file__)
        mocks_dir = os.path.join(base_dir, "mocks")
        # Keys must be the exact module path, not the import statement
        all_targets = {
            "google.adk.agents.llm_agent": os.path.join(mocks_dir, "llm_agent.py"),
            "google.adk.runners": os.path.join(mocks_dir, "runners.py"),
            "google.adk.sessions.in_memory_session_service": os.path.join(mocks_dir, "in_memory_session_service.py"),
            "google.genai.types": os.path.join(mocks_dir, "types.py")
        }
        if fullname in all_targets:
            return importlib.util.spec_from_file_location(
                name=fullname,
                location=all_targets[fullname]
            )
        return None