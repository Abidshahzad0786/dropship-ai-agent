import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re

# Page Configuration
st.set_page_config(
    page_title="AI Dropship Agent",
    page_icon="🛍️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #1E88E5; text-align: center; }
    .sub-text { font-size: 14px; color: #666; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛍️ Global AI Dropshipping Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">CJ Dropshipping & Multi-Site Auto Product Importer</div>', unsafe_allow_html=True)

# Sidebar Settings
st.sidebar.header("⚙️ سیٹنگز (Settings)")

platform = st.sidebar.selectbox(
    "ٹارگٹ پلیٹ فارم منتخب کریں:",
    ["TikTok Shop Seller", "Shopify", "WooCommerce", "General CSV / Excel"]
)

target_country = st.sidebar.selectbox(
    "ٹارگٹ ملک اور کرنسی:",
    ["Philippines (PHP ₱)", "USA (USD $)", "UAE (AED د.إ)", "UK (GBP £)", "Saudi Arabia (SAR ر.س)", "Pakistan (PKR ₨)"]
)

groq_api_key = st.sidebar.text_input(
    "Groq Free AI Key (Llama-3):",
    type="password",
    help="Console.groq.com سے بالکل فری کی ملتی ہے"
)

profit_margin = st.sidebar.slider("منافع مارجن (Profit Margin %):", 10, 200, 50)

# Scraper Function
def scrape_product(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Title Extraction
        title = ""
        if soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            title = soup.find('title').get_text(strip=True)
        
        # Image Extraction
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = url.rstrip('/') + src
                if src not in images and not any(junk in src.lower() for junk in ['logo', 'icon', 'avatar', 'badge']):
                    images.append(src)
        
        # Text/Specs Extraction
        text_content = ""
        for p in soup.find_all(['p', 'li', 'span']):
            t = p.get_text(strip=True)
            if len(t) > 20:
                text_content += t + "\n"
                
        return {
            "title": title or "Product Title Found",
            "images": images[:8],
            "raw_text": text_content[:3000]
        }
    except Exception as e:
        return {"error": str(e)}

# AI Processing Function
def process_with_ai(raw_title, raw_text, images, platform, country, api_key):
    if not api_key:
        # Fallback simulation if no API key
        return {
            "clean_title": f"🔥 Premium {raw_title[:45]}",
            "html_description": f"""
            <h3>✨ Super High Quality Product</h3>
            <p>Elevate your lifestyle with this must-have item. Perfect for everyday use with premium durability.</p>
            {f'<img src="{images[0]}" style="width:100%; border-radius:10px; margin:10px 0;">' if images else ''}
            <h4>🌟 Top Features:</h4>
            <ul>
                <li>✅ High Quality Premium Material</li>
                <li>✅ 100% Brand New & Verified Design</li>
                <li>✅ Perfect Fit & Easy to Use</li>
                <li>✅ Fast Shipping & Safe Packaging</li>
            </ul>
            {f'<img src="{images[1]}" style="width:100%; border-radius:10px; margin:10px 0;">' if len(images)>1 else ''}
            <h4>📦 Package Includes:</h4>
            <p>1x Complete Set (Ready to Use)</p>
            """
        }
    
    from groq import Groq
    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are an expert E-Commerce Dropshipping Copywriter for {platform} in {country}.
    Clean up this supplier data. Remove ugly specification tables, messy columns, and supplier junk.
    Write high-converting, visually rich, catchy copy formatted with HTML.
    
    Product Title: {raw_title}
    Raw Info: {raw_text}
    
    Available Images to embed:
    {json.dumps(images[:4])}
    
    Rules:
    1. Make an attractive, short, SEO-friendly Title.
    2. Write an exciting HTML description with 4 emojis bullet points.
    3. EMBED the provided image URLs cleanly inside the HTML description using <img src="..." style="width:100%; border-radius:8px; margin:10px 0;" /> tags between sections.
    4. Return ONLY valid JSON format:
    {{
        "clean_title": "New Catchy Title Here",
        "html_description": "Full HTML description with embedded image tags"
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# Main UI
product_url = st.text_input("🔗 پروڈکٹ کا لنک یہاں پیسٹ کریں (CJ Dropshipping / Any Web Link):", placeholder="https://...")

if st.button("🚀 ڈیٹا لائیں اور AI سے ڈسکرپشن بنائیں"):
    if not product_url:
        st.warning("براہ کرم پہلے پروڈکٹ کا لنک داخل کریں۔")
    else:
        with st.spinner("ویب سائٹ سے ڈیٹا اور تصاویر نکالی جا رہی ہیں..."):
            data = scrape_product(product_url)
            
            if "error" in data:
                st.error(f"Error fetching product: {data['error']}")
            else:
                st.success("✅ پروڈکٹ ڈیٹا اور تصاویر کامیابی سے نکال لی گئیں!")
                
                with st.spinner("AI مواد کو صاف اور تیار کر رہا ہے..."):
                    ai_result = process_with_ai(
                        data["title"], 
                        data["raw_text"], 
                        data["images"], 
                        platform, 
                        target_country, 
                        groq_api_key
                    )
                    
                    st.divider()
                    st.subheader("🎯 تیار شدہ ٹائٹل (Optimized Title):")
                    st.text_input("Title", value=ai_result.get("clean_title", data["title"]), label_visibility="collapsed")
                    
                    st.subheader("🖼️ پروڈکٹ گیلری (Gallery Images):")
                    if data["images"]:
                        cols = st.columns(min(len(data["images"]), 4))
                        for idx, img_url in enumerate(data["images"][:4]):
                            with cols[idx]:
                                st.image(img_url, use_container_width=True)
                    
                    st.subheader("📝 ڈسکرپشن کا لائیو پریویو (تصاویر کے ساتھ):")
                    st.components.v1.html(ai_result.get("html_description", ""), height=450, scrolling=True)
                    
                    with st.expander("📋 کاپی کرنے کے لیے مکمل HTML کوڈ دیکھیں"):
                        st.code(ai_result.get("html_description", ""), language="html")
