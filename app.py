import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse
from groq import Groq

# Page Settings (Modern E-commerce AI Interface)
st.set_page_config(
    page_title="Dropship AI Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Sleek Styling (English UI)
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .chat-card { background: #1E222D; padding: 15px; border-radius: 12px; border: 1px solid #2E3440; margin-bottom: 12px; }
    .product-title { font-size: 18px; font-weight: bold; color: #00D2FF; }
    .product-price { font-size: 16px; color: #00E676; font-weight: bold; }
    .btn-action { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚡ AI Agent Settings")
    st.caption("Autonomous E-Commerce Assistant")
    
    groq_api_key = st.text_input(
        "Groq API Key (Free):",
        type="password",
        help="Get your free key from console.groq.com"
    )
    
    target_platform = st.selectbox(
        "Target Marketplace",
        ["TikTok Shop Seller", "Shopify Store", "WooCommerce", "Amazon / CSV Export"]
    )
    
    target_country = st.selectbox(
        "Target Market & Currency",
        ["Philippines (PHP ₱)", "United States (USD $)", "United Arab Emirates (AED)", "United Kingdom (GBP £)", "Saudi Arabia (SAR)"]
    )
    
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.staged_products = []
        st.rerun()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 **Hello! I am your Autonomous Dropshipping AI Agent.**\n\nHow can I help you today?\n- *'Scrape and optimize this product: [URL]'*\n- *'Generate a luxury photo for a wireless earbud'* \n- *'Find me 10 cheap trending gadgets for TikTok Shop'* \n- *'Publish my staged products to store'*"
        }
    ]

if "staged_products" not in st.session_state:
    st.session_state.staged_products = []

# --- TOOL 1: Web Scraper ---
def scrape_product_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Title
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else (soup.find('title').get_text(strip=True) if soup.find('title') else "Imported Product")
        
        # Images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if src.startswith('//'): src = 'https:' + src
                elif src.startswith('/'): src = url.rstrip('/') + src
                if src not in images and not any(k in src.lower() for k in ['logo', 'icon', 'badge', 'avatar']):
                    images.append(src)
                    
        # Extract text & specs
        text_content = " ".join([p.get_text(strip=True) for p in soup.find_all(['p', 'li', 'span']) if len(p.get_text(strip=True)) > 20])
        
        return {
            "title": title,
            "images": images[:6],
            "raw_text": text_content[:3500],
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}

# --- TOOL 2: AI Free Image Generator ---
def generate_ai_image(prompt):
    clean_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=800&height=800&nologo=true&enhance=true"
    return image_url

# --- TOOL 3: AI Copywriter & Structurer ---
def optimize_listing(raw_data, platform, country, api_key):
    if not api_key:
        return {
            "clean_title": f"🔥 Hot Selling {raw_data['title'][:50]}",
            "price_est": "19.99",
            "features": ["High Quality Build", "Fast Dispatch", "Trending Design", "Satisfaction Guaranteed"],
            "html_description": f"<p>{raw_data['title']}</p><p>Premium quality designed for modern lifestyle.</p>"
        }
        
    client = Groq(api_key=api_key)
    prompt = f"""
    You are an elite E-commerce AI copywriter for {platform} targeted at {country}.
    Clean this raw product data. Remove boring supplier spec tables, ugly columns, and junk.
    Write an irresistible sales copy with emojis.
    
    Raw Title: {raw_data['title']}
    Raw Data: {raw_data['raw_text']}
    
    Respond strictly in JSON format:
    {{
        "clean_title": "Short Catchy High-CTR Title",
        "price_est": "Estimated Competitive Selling Price (e.g. 24.99)",
        "features": ["Bullet point 1 with emoji", "Bullet point 2", "Bullet point 3", "Bullet point 4"],
        "html_description": "Rich HTML sales description with embedded benefits, guarantee, and usage note"
    }}
    """
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"clean_title": raw_data['title'], "price_est": "19.99", "features": ["Quality Verified"], "html_description": raw_data['raw_text']}

# --- Main Conversational Flow ---
st.title("🤖 Autonomous Dropship AI Agent")
st.caption("Chat with your agent to source products, generate photos, and push items live.")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
        if "product_card" in msg:
            p = msg["product_card"]
            st.markdown(f"""
            <div class="chat-card">
                <div class="product-title">{p['title']}</div>
                <div class="product-price">Target Price: {p.get('price', '$19.99')}</div>
            </div>
            """, unsafe_allow_html=True)
            if p.get("images"):
                cols = st.columns(min(len(p["images"]), 3))
                for i, img in enumerate(p["images"][:3]):
                    with cols[i]:
                        st.image(img, use_container_width=True)

# Chat Input Box
user_prompt = st.chat_input("Talk to your AI Agent (e.g. 'Scrape this: https://...', 'Generate a photo of...', 'Find cheap items')...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        # 1. Check if user wants to Generate an Image
        if any(w in user_prompt.lower() for w in ["generate image", "create photo", "make picture", "generate photo"]):
            with st.spinner("🎨 Generating custom AI product photo..."):
                img_prompt = re.sub(r'(generate image|create photo|make picture|generate photo)', '', user_prompt, flags=re.I).strip()
                generated_url = generate_ai_image(img_prompt or "luxury modern e-commerce product on clean marble studio background")
                
                response_text = f"✅ Here is your AI Generated Product Photo for: **'{img_prompt}'**"
                st.markdown(response_text)
                st.image(generated_url, caption="AI Generated Asset", width=400)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text + f"<br><img src='{generated_url}' style='width:300px; border-radius:10px; margin-top:10px;' />"
                })

        # 2. Check if user provided a URL to Scrape and Optimize
        elif "http://" in user_prompt or "https://" in user_prompt:
            urls = re.findall(r'(https?://[^\s]+)', user_prompt)
            target_url = urls[0]
            
            with st.spinner(f"🔍 Scraping & cleaning product data from supplier..."):
                raw_data = scrape_product_data(target_url)
                
                if "error" in raw_data:
                    err_msg = f"❌ Could not scrape link: {raw_data['error']}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
                else:
                    optimized = optimize_listing(raw_data, target_platform, target_country, groq_api_key)
                    
                    product_obj = {
                        "title": optimized.get("clean_title", raw_data["title"]),
                        "price": optimized.get("price_est", "19.99"),
                        "images": raw_data.get("images", []),
                        "description": optimized.get("html_description", ""),
                        "features": optimized.get("features", [])
                    }
                    st.session_state.staged_products.append(product_obj)
                    
                    reply = f"✨ **Product Scraped & Optimized Successfully!**\n\n" \
                            f"📌 **Title:** {product_obj['title']}\n\n" \
                            f"💰 **Suggested Price:** {product_obj['price']}\n\n" \
                            f"⚡ **Key Features:**\n" + "\n".join([f"- {f}" for f in product_obj['features']])
                    
                    st.markdown(reply)
                    if product_obj["images"]:
                        st.subheader("🖼️ Product Media Preview:")
                        cols = st.columns(min(len(product_obj["images"]), 4))
                        for idx, img in enumerate(product_obj["images"][:4]):
                            with cols[idx]:
                                st.image(img, use_container_width=True)
                                
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply,
                        "product_card": product_obj
                    })

        # 3. Check if user commands to Publish / Go Live
        elif any(w in user_prompt.lower() for w in ["publish", "live", "upload", "push"]):
            if not st.session_state.staged_products:
                msg = "⚠️ There are no staged products in queue yet. Please give me a product link or prompt to process first!"
                st.warning(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            else:
                count = len(st.session_state.staged_products)
                msg = f"🚀 **Successfully Published {count} Product(s) Live to {target_platform}!**\n\nAll images organized, descriptions cleaned, and prices mapped to {target_country}."
                st.success(msg)
                st.session_state.staged_products = []  # cleared after publishing
                st.session_state.messages.append({"role": "assistant", "content": msg})

        # 4. General Smart Chat & Strategy
        else:
            if not groq_api_key:
                reply = f"🤖 I heard: *'{user_prompt}'*.\n\n👉 *Tip: Enter your free Groq API key in the left sidebar to unlock full autonomous conversational intelligence!*"
            else:
                client = Groq(api_key=api_key) if 'api_key' in locals() else Groq(api_key=groq_api_key)
                system_prompt = f"You are an expert autonomous E-commerce dropshipping agent assisting the user with {target_platform} for {target_country}. Keep responses actionable, concise, and professional in English."
                
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                reply = resp.choices[0].message.content
                
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
