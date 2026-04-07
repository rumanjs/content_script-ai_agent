import os
import google.generativeai as genai
from . import schemas
from typing import Dict, List
from dotenv import load_dotenv
import json
from datetime import timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

load_dotenv()

# Configure the Gemini API client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Prompt templates for each platform
PROMPT_TEMPLATES = {
    "Instagram Reel": "Generate an Instagram Reel script with a hook (first 3 seconds), main content, and a call to action. Also provide a short caption and relevant hashtags. Use the following inputs: Topic: {topic}, Audience: {audience}, Duration: {duration}, Tone: {tone}. IMPORTANT: MUST BE WRITTEN ENTIRELY IN THE FOLLOWING LANGUAGE: {language}. Ensure proper Unicode handling.",
    "YouTube": "Generate a YouTube video script including hook, introduction, main explanation, example, and call to action. Also suggest a video title. Use inputs: Topic: {topic}, Audience: {audience}, Duration: {duration}, Tone: {tone}. IMPORTANT: MUST BE WRITTEN ENTIRELY IN THE FOLLOWING LANGUAGE: {language}. Ensure proper Unicode handling.",
    "Facebook": "Create a Facebook post with engaging text, a short storytelling style, call to action, and hashtags. Use inputs: Topic: {topic}, Audience: {audience}, Tone: {tone}. IMPORTANT: MUST BE WRITTEN ENTIRELY IN THE FOLLOWING LANGUAGE: {language}. Ensure proper Unicode handling.",
    "WhatsApp": "Write a concise WhatsApp message (including emojis) for promotion or information. Use inputs: Topic: {topic}, Audience: {audience}, Tone: {tone}. IMPORTANT: MUST BE WRITTEN ENTIRELY IN THE FOLLOWING LANGUAGE: {language}. Ensure proper Unicode handling.",
    "Telegram": "Compose a detailed Telegram channel post with bullet points, call to action, and hashtags. Use inputs: Topic: {topic}, Audience: {audience}, Tone: {tone}. IMPORTANT: MUST BE WRITTEN ENTIRELY IN THE FOLLOWING LANGUAGE: {language}. Ensure proper Unicode handling."
}

async def generate_content(request: schemas.GenerateRequest) -> schemas.GenerateResponse:
    platform = request.platform
    template = PROMPT_TEMPLATES.get(platform)
    if not template:
        raise ValueError(f"Unsupported platform: {platform}")
    prompt = template.format(
        topic=request.topic,
        audience=request.audience,
        duration=request.duration or "",
        language=request.language,
        tone=request.tone,
    )
    # Call Gemini GenerativeModel
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = await model.generate_content_async(prompt)
    content_text = response.text.strip()
    # Simple parsing – split by lines for hook, script, etc.
    # For demonstration, we place the whole text in the script field.
    platform_content = schemas.PlatformContent(
        script=content_text,
        hook=None,
        caption=None,
        hashtags=None,
        title=None,
        cta=None,
    )
    return schemas.GenerateResponse(platform=platform, content=platform_content)

async def generate_hook(request: schemas.HookRequest) -> schemas.HookResponse:
    prompt = f"Generate a catchy and engaging hook (1-2 sentences max) for a content piece. Topic: {request.topic}, Platform: {request.platform}. IMPORTANT: MUST BE WRITTEN ENTIRELY IN THE FOLLOWING LANGUAGE: {request.language}. Ensure proper Unicode handling."
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = await model.generate_content_async(prompt)
    return schemas.HookResponse(hook=response.text.strip())

async def generate_calendar(request: schemas.CalendarRequest) -> schemas.CalendarResponse:
    platform = request.platform
    template = PROMPT_TEMPLATES.get(platform)
    if not template:
        raise ValueError(f"Unsupported platform: {platform}")
        
    prompt = f"Generate {request.post_count} distinct content pieces for {platform}. Each piece should follow this instruction: {template.format(topic=request.topic, audience=request.audience, duration='', language=request.language, tone=request.tone)}. Output the response as a valid JSON array of strings, where each string is the full content for one post. Do NOT include any markdown code block formatting in your response. Just the raw JSON array."
    
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    response = await model.generate_content_async(prompt)
    
    try:
        posts_text = json.loads(response.text.strip())
    except json.JSONDecodeError:
        # Fallback if the model didn't return valid JSON
        posts_text = [response.text.strip()] * request.post_count
        
    posts = []
    current_date = request.start_date
    for text in posts_text:
        platform_content = schemas.PlatformContent(
            script=text,
            hook=None,
            caption=None,
            hashtags=None,
            title=None,
            cta=None,
        )
        posts.append(schemas.CalendarResponseElement(
            scheduled_date=current_date,
            content=platform_content
        ))
        current_date += timedelta(days=1)
        
    return schemas.CalendarResponse(platform=platform, posts=posts)

def generate_pdf(text_content: str) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Try using a font that supports more characters, but Helvetica is default
    c.setFont("Helvetica", 12)
    lines = text_content.split('\n')
    
    y = height - 40
    for line in lines:
        # handle line wrapping for simpleSplit
        wrapped_lines = simpleSplit(line, 'Helvetica', 12, width - 80)
        for w_line in wrapped_lines:
            c.drawString(40, y, w_line)
            y -= 15
            if y < 40:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 40
                
    c.save()
    buffer.seek(0)
    return buffer
