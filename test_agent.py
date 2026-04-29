import asyncio
from app.agents.agent_manager import agent_manager

async def test():
    print("Testing hello...")
    res = agent_manager.run_agent(agent_manager.main_agent, "hello")
    print(f"Hello response: {res}")
    
    print("Testing full workflow...")
    res = agent_manager.run_full_event_workflow(user_id="user123", event_name="Test Event")
    print(f"Workflow response: {res}")

if __name__ == "__main__":
    asyncio.run(test())
