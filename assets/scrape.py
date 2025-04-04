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
    prompt = f"[INST] Create blog post with 3 features and CTA about: {tool_data} [/INST]"  
    response = requests.post(HF_API, headers=HF_HEADERS, json={"inputs": prompt})  
    return response.json()[0]['generated_text'].split("[/INST]")[-1].strip()  

def light_post(source, content):  
    """Generate 2 no-AI posts/day"""  
    cta = "🔥 Trending Now →" if source == "ProductHunt" else "💬 Community Pick →"  
    return f"""**From {source}**:  
*{content[:200]}...*  

{cta} [Try Tool]({{% raw %}}{{{{ page.affiliate_link }}}{{% endraw %}})  
"""  

# Main script  
ph_feed = feedparser.parse('https://www.producthunt.com/feed/collection/ai-tools')  
reddit_feed = feedparser.parse('https://www.reddit.com/r/AITools/new/.rss')  

# Process 3 posts/day (1 AI + 2 light)  
for i, entry in enumerate(ph_feed.entries[:1] + reddit_feed.entries[:2]):  
    date_str = datetime.today().strftime('%Y-%m-%d')  
    filename = f"_posts/{date_str}-post{i}.md"  
    affiliate_link = f"{entry.link}{'?ref=autoverse' if 'producthunt' in entry.link else ''}"  

    if i == 0:  # AI post  
        content = ai_post(f"{entry.title}: {entry.summary}")  
    else:       # Light posts  
        source = "ProductHunt" if i ==1 else "Reddit"  
        content = light_post(source, entry.summary)  

    with open(filename, 'w') as f:  
        f.write(f"""---  
layout: post  
title: "{re.sub(r'\b(launch|new)\b', '🚀 \g<0>', entry.title, flags=re.I)}"  
affiliate_link: "{affiliate_link}"  
---  

{content}  
""")  
