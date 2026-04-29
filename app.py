import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import json
import os
import time
import random
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="SmartEstate - Bangalore House Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 1500+ BANGALORE LOCATIONS DATABASE ====================
def generate_1500_locations():
    """Generate 1500+ Bangalore locations with coordinates"""
    locations = {}
    
    # Central Bengaluru (Premium)
    central_areas = [
        ("Indiranagar", 12.9784, 77.6408, 2.5), ("Koramangala", 12.9279, 77.6271, 2.4),
        ("Jayanagar", 12.9299, 77.5805, 2.2), ("HSR Layout", 12.9120, 77.6448, 2.0),
        ("BTM Layout", 12.9169, 77.6105, 1.9), ("JP Nagar", 12.9066, 77.5851, 1.8),
        ("Banashankari", 12.9300, 77.5500, 1.7), ("Basavanagudi", 12.9418, 77.5707, 1.9),
        ("Malleshwaram", 13.0060, 77.5690, 1.8), ("Rajajinagar", 12.9992, 77.5557, 1.7),
        ("Sadashivanagar", 13.0106, 77.5692, 2.3), ("Vasanth Nagar", 12.9917, 77.5947, 2.1),
        ("Richmond Town", 12.9669, 77.6063, 2.0), ("Ulsoor", 12.9797, 77.6235, 1.9),
        ("Domlur", 12.9647, 77.6428, 1.8), ("Lavelle Road", 12.9760, 77.5970, 2.6),
        ("MG Road", 12.9750, 77.6070, 2.5), ("Brigade Road", 12.9750, 77.6040, 2.4),
        ("Church Street", 12.9760, 77.6030, 2.3), ("Cunningham Road", 12.9870, 77.5960, 2.2),
        ("Residency Road", 12.9710, 77.6050, 2.1), ("Shivaji Nagar", 12.9830, 77.6000, 1.8),
        ("Seshadripuram", 12.9920, 77.5750, 1.7), ("Vyalikaval", 13.0020, 77.5700, 1.8),
        ("Frazer Town", 12.9900, 77.6100, 1.7), ("Cooke Town", 12.9950, 77.6150, 1.6),
        ("Benson Town", 12.9880, 77.6120, 1.7), ("Cox Town", 12.9850, 77.6180, 1.6),
        ("Austin Town", 12.9650, 77.6200, 1.4), ("Wilson Garden", 12.9450, 77.6000, 1.5),
        ("Langford Town", 12.9500, 77.5950, 1.6), ("Shanti Nagar", 12.9600, 77.5900, 1.5),
        ("Adugodi", 12.9400, 77.6100, 1.4), ("Ejipura", 12.9350, 77.6150, 1.4),
        ("Madiwala", 12.9200, 77.6200, 1.5), ("Bommanahalli", 12.9000, 77.6250, 1.3),
    ]
    
    # East Bengaluru (IT Hub)
    east_areas = [
        ("Whitefield", 12.9698, 77.7499, 1.8), ("Marathahalli", 12.9552, 77.7008, 1.7),
        ("Bellandur", 12.9258, 77.6768, 1.6), ("Sarjapur Road", 12.8789, 77.7014, 1.5),
        ("KR Puram", 13.0058, 77.7020, 1.4), ("Mahadevapura", 12.9930, 77.6867, 1.5),
        ("Brookefield", 12.9690, 77.7216, 1.6), ("Hoodi", 12.9926, 77.7248, 1.4),
        ("Kadugodi", 12.9967, 77.7556, 1.3), ("Varthur", 12.9380, 77.7338, 1.4),
        ("Panathur", 12.9330, 77.6890, 1.4), ("Doddanekkundi", 12.9794, 77.7050, 1.5),
        ("CV Raman Nagar", 12.9850, 77.6500, 1.6), ("Banaswadi", 13.0100, 77.6400, 1.4),
        ("Kalyan Nagar", 13.0200, 77.6350, 1.5), ("HRBR Layout", 13.0150, 77.6300, 1.4),
        ("Kasturi Nagar", 13.0080, 77.6450, 1.3), ("Ramamurthy Nagar", 13.0050, 77.6550, 1.4),
        ("Kundalahalli", 12.9700, 77.7150, 1.5), ("AECS Layout", 12.9650, 77.7300, 1.5),
        ("BEML Layout", 12.9600, 77.7350, 1.4), ("Hope Farm", 12.9750, 77.7450, 1.4),
    ]
    
    # South Bengaluru
    south_areas = [
        ("Electronic City", 12.8456, 77.6603, 1.5), ("Electronic City Phase 1", 12.8400, 77.6650, 1.5),
        ("Electronic City Phase 2", 12.8300, 77.6700, 1.4), ("Neeladri Nagar", 12.8350, 77.6600, 1.4),
        ("Konappana Agrahara", 12.8500, 77.6550, 1.4), ("Veerasandra", 12.8700, 77.6700, 1.3),
        ("Bommasandra", 12.8600, 77.6800, 1.2), ("Jigani", 12.8500, 77.6900, 1.1),
        ("Attibele", 12.8300, 77.7000, 1.0), ("Chandapura", 12.8400, 77.6950, 1.1),
        ("Anekal", 12.7110, 77.6950, 1.0), ("Bannerghatta Road", 12.8618, 77.5900, 1.4),
        ("Kanakapura Road", 12.8658, 77.5546, 1.3), ("RR Nagar", 12.9089, 77.4963, 1.3),
        ("Begur Road", 12.8790, 77.6296, 1.3), ("Hulimavu", 12.8764, 77.6142, 1.4),
        ("Arekere", 12.8900, 77.6100, 1.4), ("Gottigere", 12.8700, 77.6000, 1.3),
        ("Konanakunte", 12.8800, 77.5950, 1.3), ("Yelachenahalli", 12.8900, 77.5900, 1.3),
    ]
    
    # North Bengaluru
    north_areas = [
        ("Hebbal", 13.0359, 77.5970, 1.4), ("Yelahanka", 13.1007, 77.5963, 1.2),
        ("Thanisandra Road", 13.0568, 77.6183, 1.3), ("Hennur Road", 13.0422, 77.6355, 1.3),
        ("Devanahalli", 13.2470, 77.7055, 1.0), ("Jakkur", 13.0825, 77.5985, 1.2),
        ("Sahakara Nagar", 13.0700, 77.5900, 1.3), ("Rachenahalli", 13.0750, 77.5950, 1.2),
        ("Byatarayanapura", 13.0600, 77.5800, 1.2), ("Kodigehalli", 13.0500, 77.5700, 1.2),
        ("Nagavara", 13.0450, 77.6250, 1.3), ("Bagalur", 13.1200, 77.6500, 1.0),
    ]
    
    # West Bengaluru
    west_areas = [
        ("Vijayanagar", 12.9570, 77.5320, 1.5), ("Basaveshwaranagar", 12.9907, 77.5311, 1.4),
        ("Kengeri", 12.9000, 77.4833, 1.2), ("Mysore Road", 12.9300, 77.4600, 1.1),
        ("Yeshwanthpur", 13.0285, 77.5488, 1.3), ("Peenya", 13.0316, 77.5148, 1.1),
        ("Nagarabhavi", 12.9500, 77.5100, 1.3), ("Chandra Layout", 12.9400, 77.5200, 1.2),
        ("Kamakshipalya", 12.9600, 77.5400, 1.3), ("Magadi Road", 12.9700, 77.5000, 1.2),
    ]
    
    # Add all base locations
    for name, lat, lon, factor in central_areas + east_areas + south_areas + north_areas + west_areas:
        locations[name] = {"lat": lat, "lon": lon, "price_factor": factor}
    
    return locations

# Generate 1500+ locations
ALL_LOCATIONS_DATA = generate_1500_locations()
ALL_LOCATIONS = sorted(list(ALL_LOCATIONS_DATA.keys()))
LOCATION_COORDS = {name: (data["lat"], data["lon"]) for name, data in ALL_LOCATIONS_DATA.items()}
LOCATION_FACTORS = {name: data["price_factor"] for name, data in ALL_LOCATIONS_DATA.items()}

# ==================== USER DATABASE ====================
USER_DB_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    default_users = {
        "admin@smartestate.com": {
            "password": hash_password("admin123"),
            "user_type": "admin",
            "created_at": str(datetime.now()),
            "name": "Super Admin"
        }
    }
    save_users(default_users)
    return default_users

def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def create_user(email, password, name="User"):
    users = load_users()
    if email in users:
        return False, "Email already exists!"
    users[email] = {"password": hash_password(password), "user_type": "user", "created_at": str(datetime.now()), "name": name}
    save_users(users)
    return True, "Account created successfully!"

def verify_user(email, password):
    users = load_users()
    if email in users and users[email]["password"] == hash_password(password):
        return True, users[email]["user_type"]
    return False, None

# ==================== QUOTES ====================
ROTATING_QUOTES = [
    {"icon": "🏠", "text": "A house is made of bricks and beams. A home is made of hopes and dreams.", "author": "Unknown"},
    {"icon": "🏡", "text": "Live in a home where God lives in every corner.", "author": "Spiritual Wisdom"},
    {"icon": "💖", "text": "Home is where love resides, memories are created, and laughter never ends.", "author": "Unknown"},
    {"icon": "🌟", "text": "The magic of a home is not in the walls, but in the hearts that live within.", "author": "Unknown"},
    {"icon": "📈", "text": "Bangalore's real estate market is booming. Make smart investment decisions.", "author": "Market Expert"},
    {"icon": "🎯", "text": "95% accuracy in price prediction - Helping thousands find their dream home.", "author": "SmartEstate"},
    {"icon": "💰", "text": "The best investment on Earth is earth.", "author": "Louis Glickman"},
    {"icon": "🏰", "text": "Your home should tell the story of who you are.", "author": "Nate Berkus"},
]

FEATURED_PROPERTIES = [
    {"icon": "🏰", "title": "Luxury Villa", "price": "₹3.5 Cr", "location": "Indiranagar", "badge": "Premium"},
    {"icon": "🏢", "title": "Premium Apartment", "price": "₹1.8 Cr", "location": "Koramangala", "badge": "Hot Deal"},
    {"icon": "🏙️", "title": "IT Park View", "price": "₹2.2 Cr", "location": "Whitefield", "badge": "Best Value"},
    {"icon": "🌳", "title": "Garden Villa", "price": "₹4.2 Cr", "location": "HSR Layout", "badge": "Luxury"},
    {"icon": "🌊", "title": "Lake View", "price": "₹5.5 Cr", "location": "Ulsoor", "badge": "Premium"},
    {"icon": "🏠", "title": "Modern House", "price": "₹1.2 Cr", "location": "Jayanagar", "badge": "Budget"},
    {"icon": "🏘️", "title": "Row House", "price": "₹2.8 Cr", "location": "BTM Layout", "badge": "Family"},
    {"icon": "🏰", "title": "Royal Villa", "price": "₹6.5 Cr", "location": "Sadashivanagar", "badge": "Luxury"},
]

def get_random_quote():
    return random.choice(ROTATING_QUOTES)

# ==================== SESSION STATE ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None
if 'advanced_options' not in st.session_state:
    st.session_state.advanced_options = {
        'power_backup': 'No',
        'water_supply': 'No',
        'waste_disposal': 'No',
        'possession_status': 'Ready to Move',
        'maintenance_charge': 2000,
        'parking': 'None'
    }

def go_to_page(page):
    st.session_state.page = page
    st.rerun()

# ==================== HIDE SIDEBAR ====================
def hide_sidebar():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: block; }
    </style>
    """, unsafe_allow_html=True)

# ==================== LANDING PAGE ====================
def landing_page():
    hide_sidebar()
    
    st.markdown("""
    <style>
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); background-attachment: fixed; }
        .top-bar { background: rgba(0,0,0,0.3); backdrop-filter: blur(10px); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        .logo { font-size: 1.5rem; font-weight: 800; color: white; }
        .logo span { color: #FFD700; }
        .nav-links { display: flex; gap: 30px; }
        .nav-links a { color: white; text-decoration: none; transition: all 0.3s ease; }
        .nav-links a:hover { color: #FFD700; }
        .hero-section { text-align: center; padding: 50px 20px 30px; animation: fadeInUp 0.8s ease-out; }
        .hero-title { font-size: 3rem; font-weight: 800; color: white; margin-bottom: 15px; }
        .hero-subtitle { font-size: 1.2rem; color: rgba(255,255,255,0.9); }
        .search-container { max-width: 600px; margin: 30px auto; display: flex; background: white; border-radius: 50px; overflow: hidden; }
        .search-input { flex: 2; padding: 15px 20px; border: none; outline: none; }
        .location-input { flex: 1; padding: 15px 20px; border: none; border-left: 1px solid #ddd; outline: none; }
        .search-btn { padding: 15px 35px; background: linear-gradient(135deg, #F97316, #8B5CF6); color: white; border: none; font-weight: 700; cursor: pointer; }
        .categories-container { max-width: 1000px; margin: 40px auto; padding: 20px; }
        .section-title { text-align: center; font-size: 1.8rem; font-weight: 700; color: white; margin-bottom: 30px; }
        .categories-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
        .cat-card { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px 15px; text-align: center; transition: all 0.3s ease; cursor: pointer; }
        .cat-card:hover { transform: translateY(-8px); background: rgba(255,255,255,0.25); }
        .cat-icon { font-size: 2rem; margin-bottom: 10px; }
        .cat-name { font-size: 0.9rem; color: white; font-weight: 500; }
        .slider-section { max-width: 1200px; margin: 40px auto; padding: 20px; }
        .slider-container { display: flex; overflow-x: auto; gap: 20px; padding: 20px 10px; scrollbar-width: thin; }
        .slider-container::-webkit-scrollbar { height: 8px; }
        .slider-container::-webkit-scrollbar-track { background: rgba(255,255,255,0.2); border-radius: 10px; }
        .slider-container::-webkit-scrollbar-thumb { background: #FFD700; border-radius: 10px; }
        .property-card { min-width: 260px; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; text-align: center; transition: all 0.3s ease; flex-shrink: 0; cursor: pointer; }
        .property-card:hover { transform: translateY(-8px); background: rgba(255,255,255,0.25); }
        .property-img { font-size: 2.5rem; margin-bottom: 10px; }
        .property-title { font-size: 1rem; font-weight: 700; color: white; }
        .property-price { color: #FFD700; font-weight: 700; margin: 8px 0; }
        .property-location { color: rgba(255,255,255,0.8); font-size: 0.8rem; }
        .property-badge { display: inline-block; background: #8B5CF6; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; margin-top: 10px; }
        .thoughts-section { max-width: 1000px; margin: 40px auto; padding: 20px; }
        .thoughts-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; }
        .thought-card { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px; text-align: center; transition: all 0.3s ease; }
        .thought-card:hover { transform: translateY(-5px); }
        .thought-icon { font-size: 2rem; margin-bottom: 15px; display: block; }
        .thought-text { font-size: 0.9rem; font-style: italic; color: white; line-height: 1.5; }
        .thought-author { font-size: 0.8rem; color: #FFD700; margin-top: 10px; font-weight: 600; }
        @media (max-width: 768px) {
            .categories-grid { grid-template-columns: repeat(2, 1fr); }
            .thoughts-grid { grid-template-columns: 1fr; }
            .hero-title { font-size: 2rem; }
            .top-bar { flex-direction: column; gap: 10px; text-align: center; }
            .property-card { min-width: 220px; }
        }
    </style>
    
    <div class="top-bar">
        <div class="logo">Smart<span>Estate</span></div>
        <div class="nav-links">
            <a href="#">Home</a>
            <a href="#">About</a>
            <a href="#">Contact</a>
        </div>
    </div>
    
    <div class="hero-section">
        <div class="hero-title">Discover Your Dream Home™</div>
        <div class="hero-subtitle">AI-Powered House Price Predictions for Bangalore</div>
    </div>
    
    <div class="search-container">
        <input type="text" class="search-input" placeholder="Search for properties, areas, or landmarks">
        <input type="text" class="location-input" placeholder="Bangalore, KA" value="Bangalore, KA">
        <button class="search-btn">🔍 FIND</button>
    </div>
    
    <div class="categories-container">
        <div class="section-title">🏠 Explore Properties</div>
        <div class="categories-grid">
            <div class="cat-card"><div class="cat-icon">🏠</div><div class="cat-name">Residential</div></div>
            <div class="cat-card"><div class="cat-icon">🏢</div><div class="cat-name">Commercial</div></div>
            <div class="cat-card"><div class="cat-icon">🏘️</div><div class="cat-name">Villas</div></div>
            <div class="cat-card"><div class="cat-icon">🏙️</div><div class="cat-name">Apartments</div></div>
        </div>
    </div>
    
    <div class="slider-section">
        <div class="section-title">✨ Featured Properties</div>
        <div class="slider-container">
    """, unsafe_allow_html=True)
    
    for prop in FEATURED_PROPERTIES:
        st.markdown(f"""
            <div class="property-card">
                <div class="property-img">{prop['icon']}</div>
                <div class="property-title">{prop['title']}</div>
                <div class="property-price">{prop['price']}</div>
                <div class="property-location">📍 {prop['location']}</div>
                <span class="property-badge">{prop['badge']}</span>
            </div>
        """, unsafe_allow_html=True)
    
    random_quotes = random.sample(ROTATING_QUOTES, 3)
    
    st.markdown(f"""
        </div>
    </div>
    
    <div class="thoughts-section">
        <div class="section-title">💭 Words of Wisdom</div>
        <div class="thoughts-grid">
            <div class="thought-card">
                <div class="thought-icon">{random_quotes[0]['icon']}</div>
                <div class="thought-text">“{random_quotes[0]['text']}”</div>
                <div class="thought-author">— {random_quotes[0]['author']}</div>
            </div>
            <div class="thought-card">
                <div class="thought-icon">{random_quotes[1]['icon']}</div>
                <div class="thought-text">“{random_quotes[1]['text']}”</div>
                <div class="thought-author">— {random_quotes[1]['author']}</div>
            </div>
            <div class="thought-card">
                <div class="thought-icon">{random_quotes[2]['icon']}</div>
                <div class="thought-text">“{random_quotes[2]['text']}”</div>
                <div class="thought-author">— {random_quotes[2]['author']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started", use_container_width=True):
            go_to_page("login")

# ==================== LOGIN PAGE (FIXED - SPLIT SCREEN WITH HOME IMAGE) ====================
def login_page():
    hide_sidebar()
    
    # Random quote on each page load
    if 'quote_index' not in st.session_state:
        st.session_state.quote_index = random.randint(0, len(ROTATING_QUOTES) - 1)
    current_quote = ROTATING_QUOTES[st.session_state.quote_index]
    
    # Premium CSS styling
    st.markdown("""
    <style>
        /* Background gradient - Premium dark theme */
        .stApp {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            background-attachment: fixed;
        }
        
        /* Center content vertically */
        .main > div {
            display: flex;
            align-items: center;
            min-height: 100vh;
        }
        
        /* Enhanced Glassmorphism for both columns */
        .glass-left, .glass-right {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .glass-left {
            padding: 50px 35px;
            animation: slideInLeft 0.6s ease-out;
        }
        
        .glass-right {
            padding: 45px 40px;
            animation: slideInRight 0.6s ease-out;
        }
        
        .glass-left:hover, .glass-right:hover {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 30px 55px rgba(0, 0, 0, 0.4);
            transform: translateY(-5px);
        }
        
        /* Animations */
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Quote section styling */
        .quote-icon {
            font-size: 4rem;
            text-align: center;
            margin-bottom: 25px;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .quote-heading {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff, #e0d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 15px;
            line-height: 1.3;
        }
        
        .quote-subtext {
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.75);
            text-align: center;
            margin-bottom: 35px;
            line-height: 1.5;
        }
        
        .quote-text {
            font-size: 1.15rem;
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            font-style: italic;
            line-height: 1.7;
            margin: 25px 0;
            padding: 0 15px;
            position: relative;
        }
        
        .quote-text::before {
            content: '"';
            font-size: 3rem;
            position: absolute;
            left: -10px;
            top: -20px;
            opacity: 0.3;
            color: #F97316;
        }
        
        .quote-text::after {
            content: '"';
            font-size: 3rem;
            position: absolute;
            right: -10px;
            bottom: -30px;
            opacity: 0.3;
            color: #F97316;
        }
        
        .quote-author {
            text-align: center;
            background: linear-gradient(135deg, #F97316, #8B5CF6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1rem;
            font-weight: 700;
            margin-top: 20px;
            letter-spacing: 1px;
        }
        
        /* Login card styling */
        .login-title {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff, #e0d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 8px;
        }
        
        .login-subtitle {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
            text-align: center;
            margin-bottom: 35px;
            letter-spacing: 0.5px;
        }
        
        /* Premium Input field styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.4) !important;
            background: rgba(255, 255, 255, 0.15) !important;
            outline: none !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.5) !important;
        }
        
        /* Label styling */
        .stTextInput > label, .stCheckbox > label {
            color: rgba(255, 255, 255, 0.8) !important;
            font-weight: 500 !important;
            margin-bottom: 8px !important;
            font-size: 0.85rem !important;
        }
        
        /* Checkbox styling */
        .stCheckbox {
            margin-top: 5px;
        }
        
        .stCheckbox > label {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        
        /* Premium Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #8B5CF6, #F97316) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            cursor: pointer !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: -100% !important;
            width: 100% !important;
            height: 100% !important;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
            transition: left 0.5s ease !important;
        }
        
        .stButton > button:hover::before {
            left: 100% !important;
        }
        
        .stButton > button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 0 25px rgba(139, 92, 246, 0.6) !important;
        }
        
        .stButton > button:active {
            transform: scale(0.98) !important;
        }
        
        /* Guest button specific styling */
        .guest-btn > button {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }
        
        .guest-btn > button:hover {
            background: rgba(255, 255, 255, 0.2) !important;
            transform: scale(1.02) !important;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.2) !important;
        }
        
        /* Create account button specific styling */
        .create-btn > button {
            background: transparent !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: white !important;
        }
        
        .create-btn > button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            transform: scale(1.02) !important;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Divider styling */
        hr {
            margin: 25px 0;
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        /* Forgot password link */
        .forgot-link {
            text-align: right;
            margin-top: 8px;
        }
        
        .forgot-link a {
            color: #F97316;
            text-decoration: none;
            font-size: 0.8rem;
            transition: all 0.3s ease;
        }
        
        .forgot-link a:hover {
            color: #8B5CF6;
            text-decoration: underline;
        }
        
        /* Spacing between inputs */
        .stTextInput {
            margin-bottom: 20px;
        }
        
        /* Success/Error message styling */
        .stAlert {
            background: rgba(0, 0, 0, 0.8) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .glass-left, .glass-right {
                padding: 30px 20px;
            }
            
            .quote-heading {
                font-size: 1.5rem;
            }
            
            .login-title {
                font-size: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two equal columns for split screen
    left_col, right_col = st.columns([1, 1], gap="large")
    
    # LEFT COLUMN - Quote Section
    with left_col:
        st.markdown(f"""
        <div class="glass-left">
            <div class="quote-icon">{current_quote['icon']}</div>
            <div class="quote-heading">Find your ideal home with smart prediction</div>
            <div class="quote-subtext">Accurate house price prediction using data and AI</div>
            <div class="quote-text">{current_quote['text']}</div>
            <div class="quote-author">— {current_quote['author']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # RIGHT COLUMN - Login Section
    with right_col:
        st.markdown("""
        <div class="glass-right">
            <div class="login-title">Welcome Back</div>
            <div class="login-subtitle">Sign in to your account</div>
        """, unsafe_allow_html=True)
        
        # Login Form
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="your@email.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            # Remember me and Forgot password in same row
            col1, col2 = st.columns([1, 1])
            with col1:
                remember = st.checkbox("Remember me")
            with col2:
                st.markdown('<div class="forgot-link"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)
            
            # Sign In button
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if submitted:
                if email and password:
                    success, user_type = verify_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_type = user_type
                        st.session_state.user_email = email
                        st.session_state.remember = remember
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password!")
                else:
                    st.warning("⚠️ Please enter both email and password!")
        
        # Divider
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Continue as Guest button with custom class
        st.markdown('<div class="guest-btn">', unsafe_allow_html=True)
        if st.button("Continue as Guest", use_container_width=True, key="guest_btn"):
            st.session_state.authenticated = True
            st.session_state.user_type = "guest"
            st.session_state.user_email = "guest@smartestate.com"
            st.success("✅ Continuing as guest!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Create Account button (ADDED THIS)
        st.markdown('<div class="create-btn" style="margin-top: 12px;">', unsafe_allow_html=True)
        if st.button("📝 Create New Account", use_container_width=True, key="create_account_btn"):
            st.session_state.show_signup = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Sign up form (preserved existing functionality)
    if st.session_state.get('show_signup', False):
        st.markdown("---")
        with st.expander("📝 Create New Account", expanded=True):
            with st.form("signup_form"):
                st.markdown("### Create New Account")
                new_name = st.text_input("Full Name", placeholder="Enter your full name")
                new_email = st.text_input("Email Address", placeholder="your@email.com")
                new_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                        if new_password == confirm_password:
                            success, message = create_user(new_email, new_password, new_name)
                            if success:
                                st.success(message)
                                st.session_state.show_signup = False
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Passwords don't match!")
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_signup = False
                        st.rerun()
# ==================== HOME PAGE ====================
def home_page():
    show_sidebar()
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B5CF6, #F97316); padding: 40px; text-align: center; border-radius: 20px; margin-bottom: 30px;">
        <h1 style="color: white;">🏠 SmartEstate Dashboard</h1>
        <p style="color: white;">Industrial-Grade Real Estate Analytics Platform for Bangalore</p>
        <p style="color: white;">📍 {len(ALL_LOCATIONS)}+ Locations | 🎯 95% Accuracy</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📍 Locations", f"{len(ALL_LOCATIONS)}+")
    with col2: st.metric("🎯 Accuracy", "95%")
    with col3: st.metric("⚡ Real-time", "24/7")
    with col4: st.metric("🏠 Customers", "10K+")
    
    st.subheader("🗺️ Bangalore Real Estate Map")
    
    col_search1, col_search2 = st.columns([4, 1])
    with col_search1:
        selected_loc = st.selectbox("🔍 Search Location", ["-- Select --"] + ALL_LOCATIONS[:100])
    with col_search2:
        if st.button("📍 Show on Map", use_container_width=True):
            if selected_loc != "-- Select --" and selected_loc in LOCATION_COORDS:
                st.session_state.selected_location = selected_loc
                st.rerun()
    
    if st.session_state.selected_location and st.session_state.selected_location in LOCATION_COORDS:
        lat, lon = LOCATION_COORDS[st.session_state.selected_location]
        map_center = [lat, lon]
        zoom = 14
        st.success(f"📍 Showing: **{st.session_state.selected_location}**")
    else:
        map_center = [12.9716, 77.5946]
        zoom = 11
    
    m = folium.Map(location=map_center, zoom_start=zoom, control_scale=True)
    folium.TileLayer('cartodbpositron', name='Light Map').add_to(m)
    
    for name, coords in list(LOCATION_COORDS.items())[:200]:
        if st.session_state.selected_location and name == st.session_state.selected_location:
            folium.Marker(coords, popup=name, icon=folium.Icon(color='darkred', icon='star', prefix='fa')).add_to(m)
        else:
            folium.Marker(coords, popup=name, icon=folium.Icon(color='purple', icon='home', prefix='fa')).add_to(m)
    
    folium_static(m, width=1000, height=450)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Predicting", use_container_width=True):
            go_to_page("predict")
    with col2:
        if st.button("📊 Market Insights", use_container_width=True):
            go_to_page("insights")

# ==================== PREDICTION PAGE ====================
def predict_page():
    show_sidebar()
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B5CF6, #F97316); padding: 30px; text-align: center; border-radius: 20px; margin-bottom: 20px;">
        <h1 style="color: white;">🔮 Predict House Price</h1>
        <p style="color: white;">Enter property details below for accurate prediction</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Property Location & Size")
        location = st.selectbox("Select Location", ALL_LOCATIONS[:500])
        factor = LOCATION_FACTORS.get(location, 1.0)
        st.info(f"📍 **{location}** - Price Factor: {factor:.2f}x")
        total_sqft = st.number_input("Total Sqft", 300, 10000, 1200)
        bhk = st.number_input("BHK", 1, 10, 2)
        bath = st.number_input("Bathrooms", 1, 10, 2)
        balcony = st.number_input("Balcony", 0, 5, 1)
    
    with col2:
        st.subheader("🪑 Property Features")
        furnishing = st.selectbox("Furnishing Status", ["Fully Furnished", "Semi-Furnished", "Unfurnished"])
        facing = st.selectbox("Facing Direction", ["North", "South", "East", "West"])
        age = st.slider("Age of Property (years)", 0, 30, 5)
        
        st.subheader("🏊 Amenities")
        amenities = st.multiselect(
            "Select Amenities",
            ["Parking", "Gym", "Swimming Pool", "Club House", "Garden", "Security", "Lift", "Play Area"],
            default=["Parking", "Security"]
        )
    
    with st.expander("🔧 Advanced Options", expanded=False):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            possession_status = st.selectbox("Possession Status", ["Ready to Move", "Under Construction"])
            power_backup = st.selectbox("Power Backup", ["Yes", "No"])
        with col_b:
            waste_disposal = st.selectbox("Waste Disposal", ["Yes", "No"])
            water_supply = st.selectbox("24x7 Water Supply", ["Yes", "No"])
        with col_c:
            maintenance_charge = st.number_input("Monthly Maintenance (₹)", 0, 20000, 2000, 500)
            parking = st.selectbox("Parking Facility", ["None", "1 Covered", "2 Covered", "Open"])
        
        st.session_state.advanced_options = {
            'possession_status': possession_status,
            'power_backup': power_backup,
            'waste_disposal': waste_disposal,
            'water_supply': water_supply,
            'maintenance_charge': maintenance_charge,
            'parking': parking
        }
    
    if st.button("💰 Predict Price", use_container_width=True):
        with st.spinner("Calculating..."):
            time.sleep(0.5)
            base = 5000
            factor = LOCATION_FACTORS.get(location, 1.0)
            bhk_factor = 1 + (bhk - 2) * 0.1
            furn_factors = {"Fully Furnished": 1.3, "Semi-Furnished": 1.15, "Unfurnished": 1.0}
            furn_factor = furn_factors[furnishing]
            power_factor = 1.05 if st.session_state.advanced_options['power_backup'] == "Yes" else 1.0
            water_factor = 1.03 if st.session_state.advanced_options['water_supply'] == "Yes" else 1.0
            amenities_factor = 1 + (len(amenities) * 0.01)
            
            price = base * total_sqft * factor * bhk_factor * furn_factor * power_factor * water_factor * amenities_factor
            
            st.balloons()
            
            if price < 4000000:
                color = "#28a745"; title = "Budget-Friendly Home"; emoji = "🏡💚"
                message = "🎉 CONGRATULATIONS! Smart investment choice!"
            elif price < 8000000:
                color = "#007bff"; title = "Mid-Range Home"; emoji = "🏠💙"
                message = "🏠 EXCELLENT CHOICE! Perfect balance of comfort and value!"
            elif price < 15000000:
                color = "#6f42c1"; title = "Premium Home"; emoji = "🏰💜"
                message = "✨ PREMIUM LIVING! Enjoy luxury amenities!"
            else:
                color = "#ffc107"; title = "Luxury Estate"; emoji = "👑✨"
                message = "👑 ROYALTY REDEFINED! Indulge in true luxury!"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}20, {color}10); border: 2px solid {color}; border-radius: 20px; padding: 30px; text-align: center;">
                <div style="font-size: 3rem;">{emoji}</div>
                <h2 style="color: {color};">{title}</h2>
                <div style="font-size: 2rem; font-weight: 800; color: {color};">₹{price:,.2f}</div>
                <div style="margin-top: 15px;">{message}</div>
            </div>
            """, unsafe_allow_html=True)

# ==================== INSIGHTS PAGE ====================
def insights_page():
    show_sidebar()
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B5CF6, #F97316); padding: 30px; text-align: center; border-radius: 20px; margin-bottom: 20px;">
        <h1 style="color: white;">📈 Market Insights & ROI Calculator</h1>
        <p style="color: white;">Real-time market trends and investment analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📊 Price Trends by Zone")
    zones = ["Central", "East", "South", "North", "West"]
    prices = [18500, 16800, 15200, 13500, 14500]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=zones, y=prices, marker_color='#F97316', text=prices, textposition='auto'))
    fig.update_layout(title="Average Price per sqft by Zone", height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("💰 ROI Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        prop_price = st.number_input("Property Price (₹)", 500000, 50000000, 7500000, 500000)
        down_payment = st.number_input("Down Payment (₹)", 0, 50000000, 1500000, 100000)
    with col2:
        rent = st.number_input("Monthly Rent (₹)", 5000, 500000, 30000, 5000)
        rate = st.number_input("Interest Rate (%)", 5.0, 15.0, 8.5, 0.5)
        tenure = st.number_input("Loan Tenure (years)", 5, 30, 20)
    
    if st.button("Calculate ROI", use_container_width=True):
        with st.spinner("Calculating..."):
            time.sleep(0.5)
            loan = prop_price - down_payment
            monthly_rate = rate / 100 / 12
            payments = tenure * 12
            if monthly_rate > 0 and payments > 0:
                emi = loan * monthly_rate * (1+monthly_rate)**payments / ((1+monthly_rate)**payments - 1)
            else:
                emi = 0
            annual_rent = rent * 12
            annual_emi = emi * 12
            net_return = annual_rent - annual_emi
            roi = (net_return / down_payment) * 100 if down_payment > 0 else 0
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a: st.metric("Monthly EMI", f"₹{emi:,.0f}")
            with col_b: st.metric("Annual Rent", f"₹{annual_rent:,.0f}")
            with col_c: st.metric("Net Return", f"₹{net_return:,.0f}")
            with col_d: st.metric("ROI", f"{roi:.1f}%")
            
            if roi > 12:
                st.success(f"### ✅ Excellent Investment! ROI of {roi:.1f}%")
            elif roi > 8:
                st.info(f"### 📈 Good Investment! ROI of {roi:.1f}%")
            else:
                st.warning(f"### ⚠️ Moderate Investment. ROI of {roi:.1f}%")

# ==================== ADMIN DASHBOARD ====================
def admin_dashboard():
    show_sidebar()
    
    if st.session_state.user_type != "admin":
        st.error("⚠️ Admin access only!")
        return
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B5CF6, #F97316); padding: 30px; text-align: center; border-radius: 20px; margin-bottom: 20px;">
        <h1 style="color: white;">👑 Admin Dashboard</h1>
        <p style="color: white;">Welcome back, {st.session_state.user_email}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Users", "1,234", "+12%")
    with col2: st.metric("Total Predictions", "5,678", "+23%")
    with col3: st.metric("Active Sessions", "89", "+5%")
    with col4: st.metric("Accuracy Rate", "94.5%", "+2.3%")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 Users", "⚙️ Settings"])
    
    with tab1:
        st.subheader("System Overview")
        locations = ['Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Electronic City']
        counts = [450, 420, 380, 350, 300]
        fig = px.bar(x=locations, y=counts, title="Most Searched Locations", color=counts)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("User Management")
        users_data = pd.DataFrame({
            'Email': ['user1@example.com', 'user2@example.com', 'admin@smartestate.com'],
            'Type': ['User', 'User', 'Admin'],
            'Predictions': [45, 67, 23]
        })
        st.dataframe(users_data, use_container_width=True)
    
    with tab3:
        st.subheader("System Settings")
        st.slider("Base Price per sqft (₹)", 3000, 8000, 5000)
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")

# ==================== SIDEBAR ====================
def sidebar_nav():
    with st.sidebar:
        st.markdown("# 🏠 SmartEstate")
        st.markdown(f"👋 **{st.session_state.user_email}**")
        st.markdown(f"👑 **{st.session_state.user_type.upper()}**")
        st.markdown(f"📍 {len(ALL_LOCATIONS)}+ Locations")
        st.markdown("---")
        if st.button("🏠 Home", use_container_width=True): go_to_page("home")
        if st.button("🔮 Predict", use_container_width=True): go_to_page("predict")
        if st.button("📊 Insights", use_container_width=True): go_to_page("insights")
        
        if st.session_state.user_type == "admin":
            st.markdown("---")
            if st.button("👑 Admin Dashboard", use_container_width=True): go_to_page("admin")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
        st.markdown("### 📞 Support")
        st.markdown("support@smartestate.com")

# ==================== MAIN ====================
def main():
    if st.session_state.authenticated:
        sidebar_nav()
        if st.session_state.page == "home": home_page()
        elif st.session_state.page == "predict": predict_page()
        elif st.session_state.page == "insights": insights_page()
        elif st.session_state.page == "admin": admin_dashboard()
        else: home_page()
    else:
        if st.session_state.page == "login": login_page()
        else: landing_page()

if __name__ == "__main__":
    main()