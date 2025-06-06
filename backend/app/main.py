from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import anthropic
import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug: Print all environment variables
logger.debug("Environment variables:")
for key, value in os.environ.items():
    if 'API' in key:
        logger.debug(f"{key}: {value[:5]}...")  # Only show first 5 chars of API keys

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    logger.error("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

logger.debug(f"API Key found: {api_key[:5]}...")
client = anthropic.Anthropic(api_key=api_key)

class CloneRequest(BaseModel):
    url: str

def scrape_website(url: str) -> dict:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title
        title = soup.title.string if soup.title else ''
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else ''
        
        # Get all CSS
        css = []
        # Inline styles
        for style in soup.find_all('style'):
            css.append(style.string)
        
        # External stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                try:
                    css_url = link['href']
                    if not css_url.startswith(('http://', 'https://')):
                        # Handle relative URLs
                        from urllib.parse import urljoin
                        css_url = urljoin(url, css_url)
                    css_response = requests.get(css_url, headers=headers, timeout=5)
                    css.append(css_response.text)
                except Exception as e:
                    logger.warning(f"Failed to fetch CSS from {css_url}: {str(e)}")
        
        # Get main content
        # Try different common content containers
        main_content = None
        for selector in ['main', 'article', '#content', '.content', '#main', '.main']:
            content = soup.select_one(selector)
            if content:
                main_content = content
                break
        
        if not main_content:
            # Fallback to body if no specific container found
            main_content = soup.body
        
        # Get all images
        images = []
        for img in soup.find_all('img'):
            if img.get('src'):
                img_url = img['src']
                if not img_url.startswith(('http://', 'https://')):
                    # Handle relative URLs
                    from urllib.parse import urljoin
                    img_url = urljoin(url, img_url)
                images.append(img_url)
        
        # Get all scripts
        scripts = []
        for script in soup.find_all('script'):
            if script.get('src'):
                try:
                    script_url = script['src']
                    if not script_url.startswith(('http://', 'https://')):
                        # Handle relative URLs
                        from urllib.parse import urljoin
                        script_url = urljoin(url, script_url)
                    script_response = requests.get(script_url, headers=headers, timeout=5)
                    scripts.append(script_response.text)
                except Exception as e:
                    logger.warning(f"Failed to fetch script from {script_url}: {str(e)}")
            elif script.string:
                scripts.append(script.string)
        
        # Get all fonts
        fonts = []
        for link in soup.find_all('link', rel='stylesheet'):
            if 'fonts.googleapis.com' in link.get('href', ''):
                fonts.append(link['href'])
        
        return {
            'title': title,
            'description': description,
            'css': '\n'.join(css),
            'content': str(main_content) if main_content else '',
            'images': images,
            'scripts': scripts,
            'fonts': fonts,
            'url': url
        }
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {str(e)}")

def generate_clone(context: dict) -> str:
    try:
        # Create a detailed prompt for Claude
        prompt = f"""You are a web developer tasked with creating an exact clone of a website. Here are the details:

Title: {context['title']}
Description: {context['description']}
Original URL: {context['url']}

Content Structure:
{context['content'][:2000]}...

CSS Styles:
{context['css'][:3000]}

Images found: {', '.join(context['images'][:10])}

Fonts used: {', '.join(context['fonts'])}

Please create an HTML page that is an exact clone of the original website. Follow these guidelines:

1. Structure:
   - Maintain the exact same HTML structure and hierarchy
   - Keep all original class names and IDs
   - Preserve the semantic HTML elements
   - Include all meta tags and viewport settings

2. Styling:
   - Include all CSS styles exactly as they appear
   - Maintain the original color scheme and typography
   - Keep all animations and transitions
   - Preserve responsive design breakpoints

3. Content:
   - Keep the original content structure
   - Maintain all headings, paragraphs, and lists
   - Include all images with their original attributes
   - Preserve all links and their href attributes

4. Layout:
   - Match the original layout pixel-perfectly
   - Keep the same spacing and alignment
   - Maintain the original grid system
   - Preserve all flexbox and grid layouts

5. Responsive Design:
   - Include all media queries
   - Maintain mobile-first approach
   - Keep all responsive breakpoints
   - Preserve touch-friendly elements

Return only the complete HTML code starting with <!DOCTYPE html>. Include all necessary CSS in a <style> tag and all required scripts in <script> tags."""

        logger.debug("Sending prompt to Claude API...")
        try:
            response = client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more precise output
                system="You are a skilled web developer who specializes in creating pixel-perfect HTML clones of websites. Your goal is to create an exact replica of the original website, maintaining all styling, layout, and functionality.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            logger.debug("Received response from Claude API")
            if not response or not response.content:
                raise ValueError("Empty response from Claude API")
            return response.content[0].text
        except Exception as api_error:
            logger.error(f"Claude API error: {str(api_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Claude API error: {str(api_error)}")
            
    except Exception as e:
        logger.error(f"Error in generate_clone: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate clone: {str(e)}")

@app.get("/test-claude")
async def test_claude():
    """Test endpoint to check if Claude API is working"""
    try:
        prompt = "Say hello!"
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return {"prompt": prompt, "claude_response": response.content[0].text}
    except Exception as e:
        logger.error(f"Claude API test failed: {e}")
        return {"error": str(e)}

@app.post("/clone")
async def clone_website(request: CloneRequest):
    try:
        logger.debug(f"Received clone request for URL: {request.url}")
        
        # Scrape the website
        logger.debug("Starting website scraping...")
        context = scrape_website(request.url)
        logger.debug("Website scraping completed successfully")
        
        # Generate the clone
        logger.debug("Starting clone generation...")
        try:
            # Test the Claude API first
            logger.debug("Testing Claude API connection...")
            test_prompt = "Say hello!"
            logger.debug(f"Sending test prompt: {test_prompt}")
            test_response = client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": test_prompt}
                ]
            )
            logger.debug(f"Test response received: {test_response.content[0].text}")
            
            # Generate the clone
            cloned_html = generate_clone(context)
            logger.debug("Clone generation completed successfully")
            
            return {"html": cloned_html}
        except Exception as api_error:
            logger.error(f"Claude API error: {str(api_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to generate clone: {str(api_error)}")
            
    except Exception as e:
        logger.error(f"Error in clone_website: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-env")
async def test_env():
    """Test endpoint to check if environment variables are loaded correctly"""
    return {
        "api_key_exists": bool(os.getenv("ANTHROPIC_API_KEY")),
        "api_key_length": len(os.getenv("ANTHROPIC_API_KEY", "")),
        "api_key_prefix": os.getenv("ANTHROPIC_API_KEY", "")[:5] + "..." if os.getenv("ANTHROPIC_API_KEY") else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
