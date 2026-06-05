import io
import requests
from urllib.parse import quote
from errors import APIError

class imageModelCall:
    def __init__(self, width: int, height: int, model: str, count: int):
        self.base_url = f"https://image.pollinations.ai/prompt/{{prompt}}?width={width}&height={height}&nologo=true&model={model}"
        self.count = count
        
    def __call__(self, prompt: str):
        safe_prompt = quote(prompt)
        image_url = self.base_url.format(prompt=safe_prompt)
        response = requests.get(image_url, timeout=15)
        if response.status_code == 200:
            image_bytes = response.content
            image_stream = io.BytesIO(image_bytes)
            return image_stream
        else:
            raise APIError("500", f"Error occurred when creating the image: {response.text}")
