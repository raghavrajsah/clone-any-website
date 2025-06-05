from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
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

# Initialize Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

logger.debug(f"API Key found: {api_key[:5]}...")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

class CloneRequest(BaseModel):
    url: str

def scrape_website(url: str) -> dict:
    try:
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract important elements
        title = soup.title.string if soup.title else ''
        meta_description = soup.find('meta', {'name': 'description'})
        description = meta_description['content'] if meta_description else ''
        
        # Get all CSS
        css = []
        for style in soup.find_all('style'):
            css.append(style.string)
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                css.append(f"/* External CSS: {link['href']} */")
        
        # Get main content
        main_content = soup.find('main') or soup.find('body')
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
        else:
            content = soup.get_text(separator=' ', strip=True)
        
        return {
            'title': title,
            'description': description,
            'css': '\n'.join(css),
            'content': content,
            'html': response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {str(e)}")

def generate_clone(context: dict) -> str:
    try:
        # Simplified prompt for testing
        prompt = f"""Create a simple HTML page with this title: {context['title']}
        Include a basic style tag and some content from: {context['content'][:200]}..."""
        
        logger.debug("Sending prompt to Gemini API...")
        try:
            response = model.generate_content(prompt)
            logger.debug("Received response from Gemini API")
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            return response.text
        except Exception as api_error:
            logger.error(f"Gemini API error: {str(api_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(api_error)}")
            
    except Exception as e:
        logger.error(f"Error in generate_clone: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate clone: {str(e)}")

@app.get("/test-gemini")
async def test_gemini():
    try:
        logger.debug("Testing Gemini API connection...")
        response = model.generate_content("Say hello!")
        logger.debug(f"Gemini API response: {response.text}")
        return {"status": "success", "response": response.text}
    except Exception as e:
        logger.error(f"Gemini API test failed: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}

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
            # Test the Gemini API first
            logger.debug("Testing Gemini API connection...")
            test_prompt = "Say hello!"
            logger.debug(f"Sending test prompt: {test_prompt}")
            test_response = model.generate_content(test_prompt)
            logger.debug(f"Test response received: {test_response.text}")
            
            # Now try the actual clone
            prompt = f"""Create a simple HTML page that looks like this website:
            Title: {context['title']}
            Content: {context['content'][:500]}...
            
            Return only the HTML code starting with <!DOCTYPE html>."""
            
            logger.debug("Sending clone prompt to Gemini API...")
            response = model.generate_content(prompt)
            logger.debug("Received response from Gemini API")
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
                
            cloned_html = response.text
            logger.debug("Clone generation completed successfully")
            
            return {"html": cloned_html}
        except Exception as api_error:
            logger.error(f"Gemini API error: {str(api_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to generate clone: {str(api_error)}")
            
    except Exception as e:
        logger.error(f"Error in clone_website: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-env")
async def test_env():
    """Test endpoint to check if environment variables are loaded correctly"""
    return {
        "api_key_exists": bool(os.getenv("GOOGLE_API_KEY")),
        "api_key_length": len(os.getenv("GOOGLE_API_KEY", "")),
        "api_key_prefix": os.getenv("GOOGLE_API_KEY", "")[:5] + "..." if os.getenv("GOOGLE_API_KEY") else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
