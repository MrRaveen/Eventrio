import sys
from urllib.parse import quote

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("mcp package is required. Install via: pip install mcp", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("EventAutomationServer")

@mcp.tool()
def generate_pollinations_image(prompt: str, width: int = 1080, height: int = 1080) -> str:
    """Generate an image using Pollinations AI based on a descriptive prompt."""
    safe_prompt = quote(prompt)
    return f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&nologo=true"

@mcp.tool()
def schedule_google_calendar(event_name: str, start_time: str, end_time: str) -> str:
    """Create a real actionable Google Calendar link for scheduling an event."""
    safe_name = quote(event_name)
    # Format dates for Google Calendar (YYYYMMDDTHHMMSSZ)
    safe_start = start_time.replace("-", "").replace(":", "") + "Z"
    safe_end = end_time.replace("-", "").replace(":", "") + "Z"
    link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={safe_name}&dates={safe_start}/{safe_end}"
    return f"Created event action link. User can confirm it here: {link}"

@mcp.tool()
def send_buffer_social_post(content: str, platforms: list[str]) -> str:
    """Generate real social media intent links (Twitter/X) to publish content."""
    safe_content = quote(content)
    link = f"https://twitter.com/intent/tweet?text={safe_content}"
    return f"Prepared social media post. User can publish immediately here: {link}"

if __name__ == "__main__":
    mcp.run()
