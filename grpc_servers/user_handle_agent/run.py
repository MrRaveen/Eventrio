import asyncio
from app.routes.mainAgentAccess import serve
import os
from flask import Flask
from dotenv import load_dotenv

#only the GRPC server (not a flask server)
if __name__ == "__main__":
    load_dotenv()  
    asyncio.run(serve())
