import feedparser
import requests
import os
from datetime import datetime
import re

# Configuration
HF_API = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
USER_AGENT = "AutoverseBot/1.0 (+https://github.com/yourusername/yourrepo)"

def ai_post(tool_data):
    """Generate AI-enhanced post with conversion-focused template"""
    try:
        prompt = f"""[INST]
        Create blog post with 3 features and CTA. Rules:
        - Use only markdown formatting
        - Include "Try Now" link once
        - Add scarcity element
        - Never use HTML tags
        Input: {tool_data}
        [/INST]"""
        
        response = requests.post(HF_API, headers=HF_HEADERS, json={"inputs": prompt})
        response.raise_for_status()
        raw_content = response.json()[0]['generated_text'].split("[/INST]")[-1].strip()
        
        # Add conversion elements
        return f"""{raw_content}

**🚨 Limited Offer**: [Claim Discount →]({{{{ page.affiliate_link }}}})  
*(First 100 users only)*  

---

*Contains affiliate links. Supports our independent reviews.*
"""
        
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return f"""**Quick Summary**: {tool_data[:250]}...

[Try Now]({{{{ page.affiliate_link }}}})  
*Affiliate link included*"""

def light_post(source, content):
    """Generate minimal-effort posts"""
    cta = "🔥 Trending" if source == "ProductHunt" else "💬 Discussed"
    return f"""**From {source}**:  
*{content[:200].replace('"', "'")}...*

{cta} → [Try Tool]({{{{ page.affiliate_link }}}})  
"""

# Main execution
ph_feed = feedparser.parse(
    "https://www.producthunt.com/feed?category=ai",
    request_headers={"User-Agent": USER_AGENT}
)

reddit_feed = feedparser.parse(
    "https://www.reddit.com/r/AITools/new/.rss",
    request_headers={"User-Agent": USER_AGENT}
)

for i, entry in enumerate(ph_feed.entries[:1] + reddit_feed.entries[:2]):
    date_str = datetime.today().strftime('%Y-%m-%d')
    filename = f"_posts/{date_str}-post{i}.md"
    
    try:
        # Clean and format data
        base_url = entry.link.split('?')[0].split('#')[0]
        affiliate_link = f"{base_url}?ref=autoverse&utm_source=autoverse"
        clean_title = re.sub(r'[^\w\s-]', '', entry.title)[:75]
        decorated_title = re.sub(r'\b(launch|new|update)\b', '🚀 \\g<0>', 
                               clean_title, flags=re.I)

        # Generate content
        if i == 0:  # AI post
            content = ai_post(f"{clean_title}: {entry.summary}")
        else:       # Light posts
            source = "ProductHunt" if i == 1 else "Reddit"
            content = light_post(source, entry.summary)

        # Write post file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"""---
layout: post
title: "{decorated_title}"
affiliate_link: "{affiliate_link}"
---

{content}
""")
            
    except Exception as e:
        print(f"Failed processing {entry.get('title', 'Untitled')}: {str(e)}")
