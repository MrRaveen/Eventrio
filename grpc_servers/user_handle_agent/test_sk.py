from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions import KernelArguments, KernelPlugin, kernel_function

class MockPlugin:
    @kernel_function
    def do_something(self) -> str:
        return "mock"

settings = OpenAIChatPromptExecutionSettings()
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

plugin = KernelPlugin.from_object(plugin_instance=MockPlugin(), plugin_name="MockPlugin")

agent = ChatCompletionAgent(
    service=None,
    name="Test",
    instructions="test",
    plugins=[plugin],
    arguments=KernelArguments(settings={"default": settings})
)

import asyncio
from semantic_kernel.contents import ChatHistory

async def run():
    try:
        history = ChatHistory()
        async for m in agent.invoke(history=history):
            print(m)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(run())
