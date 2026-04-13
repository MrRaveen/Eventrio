import importlib.abc
import importlib.util
import os

class Hook(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        base_dir = os.path.dirname(__file__)
        mocks_dir = os.path.join(base_dir, "mocks")

        leaf_targets = {
            "google.adk.agents.llm_agent": "llm_agent.py",
            "google.adk.runners": "runners.py",
            "google.adk.sessions.in_memory_session_service": "in_memory_session_service.py",
            "google.genai.types": "types.py"
        }

        if fullname in leaf_targets:
            return importlib.util.spec_from_file_location(
                name=fullname,
                location=os.path.join(mocks_dir, leaf_targets[fullname])
            )
        # to intercept requests for the parent packages and hand Python 
        # an empty "dummy" package so it keeps searching down the chain.
        parent_packages = [
            "google", 
            "google.adk", 
            "google.adk.agents", 
            "google.adk.sessions",
            "google.genai"
        ]
        
        if fullname in parent_packages:
            empty_init = os.path.join(mocks_dir, "__init__.py")
            # The empty list `submodule_search_locations=[]` is critical. 
            # It tricks Python into treating this empty file as a valid, traversable Package.
            return importlib.util.spec_from_file_location(
                name=fullname,
                location=empty_init,
                submodule_search_locations=[] 
            )

        return None