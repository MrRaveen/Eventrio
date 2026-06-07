import io
import requests
from urllib.parse import quote
from errors import APIError

class imageModelCall:
    def __init__(self, width: int, height: int, model: str, count: int):
        self.url = "https://api.replicate.com/v1/models/google/imagen-4/predictions"
        self.api_key = os.getenv('IMG_KEY')
        self.count = count
        
        # Determine closest aspect ratio
        if width > height:
            self.aspect_ratio = "16:9"
        elif height > width:
            self.aspect_ratio = "9:16"
        else:
            self.aspect_ratio = "1:1"
        
    def __call__(self, prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }
        
        payload = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": self.aspect_ratio,
                "safety_filter_level": "block_only_high"
            }
        }
        
        # Increase timeout to account for image generation time
        response = requests.post(self.url, headers=headers, json=payload, timeout=60)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("status") == "succeeded" and data.get("output"):
                image_url = data["output"]
                
                # Fetch the actual image bytes to return the BytesIO stream
                img_response = requests.get(image_url, timeout=15)
                if img_response.status_code == 200:
                    image_bytes = img_response.content
                    image_stream = io.BytesIO(image_bytes)
                    return image_stream
                else:
                    raise APIError("500", f"Failed to download generated image from Replicate: {img_response.text}")
            else:
                error_msg = data.get("error", "Generation did not succeed or timed out.")
                raise APIError("500", f"Replicate API generation failed: {error_msg}")
        else:
            raise APIError(str(response.status_code), f"Error occurred when creating the image via Replicate: {response.text}")
