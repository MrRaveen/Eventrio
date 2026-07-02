import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from app.agents.core.mainAgent import MainAgent

async def test():
    m = MainAgent()
    agent = m.get_agent("123")
    print(agent)

asyncio.run(test())
