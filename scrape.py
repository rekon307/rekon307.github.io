import feedparser
import requests
import os
from datetime import datetime
import re

# Hugging Face API
HF_API = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def ai_post(tool_data):
    """Generate 1 AI-enhanced post/day"""
    try:
        prompt = f"[INST] Create blog post with 3 features and CTA about: {tool_data} [/INST]"
        response = requests.post(HF_API, headers=HF_HEADERS, json={"inputs": prompt})
        response.raise_for_status()
        return response.json()[0]['generated_text'].split("[/INST]")[-1].strip()
    except Exception as e:
        print(f"AI Post Error: {str(e)}")
        return f"**Automated Review**: {tool_data[:200]}... [Try Now]({{{{ page.affiliate_link }}}})"

def light_post(source, content):
    """Generate 2 no-AI posts/day"""
    cta = "🔥 Trending Now →" if source == "ProductHunt" else "💬 Community Pick →"
    return f"""**From {source}**:
*{content[:200].replace('"', "'")}...*

{cta} [Try Now]({{{{ page.affiliate_link }}}})
"""

# Main script
ph_feed = feedparser.parse('https://www.producthunt.com/feed/collection/ai-tools')
reddit_feed = feedparser.parse('https://www.reddit.com/r/AITools/new/.rss')

# Process 3 posts/day (1 AI + 2 light)
for i, entry in enumerate(ph_feed.entries[:1] + reddit_feed.entries[:2]):
    date_str = datetime.today().strftime('%Y-%m-%d')
    filename = f"_posts/{date_str}-post{i}.md"
    
    # Force affiliate tag on all URLs
    affiliate_link = f"{entry.link.split('?')[0]}?ref=autoverse"
    
    # Clean special characters from title
    clean_title = re.sub(r'[^\w\s-]', '', entry.title)
    decorated_title = re.sub(r'\b(launch|new)\b', '🚀 \\g<0>', clean_title, flags=re.I)

    try:
        if i == 0:  # AI post
            content = ai_post(f"{clean_title}: {entry.summary}")
        else:       # Light posts
            source = "ProductHunt" if i == 1 else "Reddit"
            content = light_post(source, entry.summary)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"""---
layout: post
title: "{decorated_title}"
affiliate_link: "{affiliate_link}"
---

{content}
""")
            
    except Exception as e:
        print(f"Error processing {entry.title}: {str(e)}")
