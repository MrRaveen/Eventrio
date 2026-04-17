def mock_dynamic_design_agent(event_data):
    # Simulating the AI interpreting the prompt "Create a cyberpunk tech event"
    return {
        "presentation": {
            "design": {
                "theme_name": "Neon Cyberpunk",
                "bg_color": "#0D0D2B",    
                "title_color": "#FF007F", 
                "text_color": "#00FFFF"  
            },
            "title": event_data.get("title", "Hackathon 2026"),
            "slides": [
                {
                    "layout": 0,
                    "header": "Welcome to the Future",
                    "sub_header": "GenAI Hackathon",
                    "body": ""
                }
            ]
        }
    }