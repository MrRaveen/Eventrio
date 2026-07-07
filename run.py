
from app import create_app
from flask_cors import CORS
app = create_app()
# Allow all origins for development (Cloudflare tunnel URLs change every session)
CORS(app, origins="*", supports_credentials=False)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
