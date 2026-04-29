# utils/styles.py
import streamlit as st

# ==================== THEME CONFIGURATION ====================
THEME_COLORS = {
    "primary": "#8B5CF6",      # Soft Purple
    "secondary": "#C4B5FD",    # Light Lavender
    "accent": "#F97316",       # Warm Orange
    "success": "#10b981",      # Green
    "warning": "#f59e0b",      # Yellow/Orange
    "danger": "#ef4444",       # Red
    "info": "#3b82f6",         # Blue
    "dark": "#1F2937",         # Dark Purple Gray
    "light": "#FFFFFF",        # White
    "background_start": "#F5F3FF",
    "background_end": "#EDE9FE",
    "glass_bg": "rgba(255, 255, 255, 0.6)",
    "glass_border": "rgba(255, 255, 255, 0.3)",
    "glass_shadow": "rgba(139, 92, 246, 0.15)",
    "glass_shadow_hover": "rgba(139, 92, 246, 0.25)"
}

# ==================== GLASSMORPHISM STYLES ====================
GLASS_CARD_STYLE = """
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 24px;
    padding: 20px;
    margin: 15px 0;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
    transition: all 0.3s ease;
"""

GLASS_CARD_HOVER_STYLE = """
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
    border-color: rgba(249, 115, 22, 0.3);
"""

BUTTON_STYLE = """
    background: linear-gradient(135deg, #8B5CF6, #F97316);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 10px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    cursor: pointer;
"""

BUTTON_HOVER_STYLE = """
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
"""

GRADIENT_TEXT_STYLE = """
    background: linear-gradient(135deg, #8B5CF6, #F97316);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
"""

# ==================== FULL SCREEN CSS STYLES ====================
def apply_fullscreen_styles():
    """Apply full-screen CSS to remove all Streamlit default styling"""
    st.markdown("""
    <style>
        /* Remove all default Streamlit padding and margins */
        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        .stAppHeader {display: none;}
        .stAppViewContainer > section:first-child {display: none;}
        .stStatusWidget {display: none;}
        
        /* Make app full height and width */
        .stApp {
            height: 100vh !important;
            width: 100% !important;
        }
        
        /* Remove all margins from containers */
        section.main > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Sidebar hidden by default */
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Remove all extra space */
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            height: 100% !important;
            width: 100% !important;
        }
        
        /* Ensure full height for all containers */
        .stAppViewContainer {
            height: 100vh !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Remove any default borders */
        .stApp {
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_custom_styles():
    """Apply custom CSS styles to the app with full theme support"""
    st.markdown(f"""
    <style>
        /* ==================== GLOBAL STYLES ==================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', sans-serif;
        }}
        
        .stApp {{
            background: linear-gradient(135deg, {THEME_COLORS['background_start']}, {THEME_COLORS['background_end']});
        }}
        
        /* ==================== TYPOGRAPHY ==================== */
        h1, h2, h3, h4, h5, h6 {{
            background: linear-gradient(135deg, {THEME_COLORS['primary']}, {THEME_COLORS['accent']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            font-family: 'Playfair Display', serif;
        }}
        
        /* ==================== GLASS CARDS ==================== */
        .glass-card {{
            {GLASS_CARD_STYLE}
        }}
        
        .glass-card:hover {{
            {GLASS_CARD_HOVER_STYLE}
        }}
        
        /* ==================== METRIC CARDS ==================== */
        .metric-card {{
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.1);
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(139, 92, 246, 0.2);
            border-color: {THEME_COLORS['accent']};
        }}
        
        .metric-number {{
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, {THEME_COLORS['primary']}, {THEME_COLORS['accent']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .metric-label {{
            color: {THEME_COLORS['dark']};
            font-size: 0.85rem;
            margin-top: 8px;
            opacity: 0.8;
        }}
        
        /* ==================== BUTTONS ==================== */
        .stButton > button {{
            {BUTTON_STYLE}
        }}
        
        .stButton > button:hover {{
            {BUTTON_HOVER_STYLE}
        }}
        
        /* ==================== INPUT FIELDS ==================== */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea > div > textarea,
        .stDateInput > div > div > input {{
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
            border-radius: 12px !important;
            padding: 10px 15px !important;
            transition: all 0.3s ease !important;
            color: {THEME_COLORS['dark']} !important;
        }}
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div:focus {{
            border-color: {THEME_COLORS['accent']} !important;
            box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2) !important;
            transform: translateY(-2px);
        }}
        
        /* ==================== SELECTBOX DROPDOWN ==================== */
        .stSelectbox div[data-baseweb="select"] > div {{
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 12px !important;
        }}
        
        /* ==================== MULTISELECT ==================== */
        .stMultiSelect [data-baseweb="select"] {{
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 12px !important;
        }}
        
        /* ==================== SLIDER ==================== */
        .stSlider > div > div > div {{
            background: linear-gradient(90deg, {THEME_COLORS['primary']}, {THEME_COLORS['accent']}) !important;
        }}
        
        .stSlider > div > div > div > div {{
            background: {THEME_COLORS['accent']} !important;
        }}
        
        /* ==================== TABS ==================== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 10px 25px;
            color: {THEME_COLORS['dark']};
            font-weight: 500;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(139, 92, 246, 0.2);
            transform: translateY(-2px);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {THEME_COLORS['primary']}, {THEME_COLORS['accent']});
            color: white !important;
            border: none;
        }}
        
        /* ==================== EXPANDER ==================== */
        .streamlit-expanderHeader {{
            background: linear-gradient(135deg, {THEME_COLORS['primary']}, {THEME_COLORS['accent']});
            border-radius: 12px;
            color: white;
            font-weight: 600;
        }}
        
        .streamlit-expanderHeader:hover {{
            transform: translateX(5px);
        }}
        
        .streamlit-expanderContent {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 0 0 12px 12px;
            padding: 20px;
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-top: none;
        }}
        
        /* ==================== ALERTS ==================== */
        .stAlert {{
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
            border-radius: 12px !important;
            border-left: 4px solid {THEME_COLORS['accent']} !important;
            animation: fadeInLeft 0.5s ease-out;
        }}
        
        @keyframes fadeInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        /* ==================== SIDEBAR ==================== */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(139, 92, 246, 0.95), rgba(196, 181, 253, 0.95));
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        [data-testid="stSidebar"] .stButton > button {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: linear-gradient(135deg, {THEME_COLORS['accent']}, {THEME_COLORS['primary']});
            border-color: transparent;
        }}
        
        /* ==================== DATAFRAME ==================== */
        .dataframe {{
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.1);
        }}
        
        /* ==================== MAP CONTAINER ==================== */
        .folium-map {{
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
            transition: all 0.3s ease;
        }}
        
        .folium-map:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
        }}
        
        /* ==================== FORM STYLING ==================== */
        .stForm {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 20px;
        }}
        
        /* ==================== CHECKBOX ==================== */
        .stCheckbox > label {{
            color: {THEME_COLORS['dark']} !important;
        }}
        
        /* ==================== RADIO BUTTONS ==================== */
        .stRadio > div {{
            gap: 10px;
        }}
        
        .stRadio > div > label {{
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 8px 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }}
        
        .stRadio > div > label:hover {{
            background: rgba(139, 92, 246, 0.2);
            transform: translateY(-2px);
        }}
        
        /* ==================== SPINNER ==================== */
        .stSpinner > div {{
            border-color: {THEME_COLORS['primary']} !important;
        }}
        
        /* ==================== SUCCESS/ERROR/WARNING ==================== */
        .stSuccess {{
            background: rgba(16, 185, 129, 0.1);
            border-left-color: #10b981;
        }}
        
        .stError {{
            background: rgba(239, 68, 68, 0.1);
            border-left-color: #ef4444;
        }}
        
        .stWarning {{
            background: rgba(245, 158, 11, 0.1);
            border-left-color: #f59e0b;
        }}
        
        .stInfo {{
            background: rgba(59, 130, 246, 0.1);
            border-left-color: #3b82f6;
        }}
        
        /* ==================== RESPONSIVE DESIGN ==================== */
        @media (max-width: 768px) {{
            .glass-card {{
                margin: 10px;
                padding: 15px;
            }}
            
            .metric-number {{
                font-size: 1.5rem;
            }}
            
            h1 {{
                font-size: 1.8rem;
            }}
            
            h2 {{
                font-size: 1.5rem;
            }}
        }}
        
        /* ==================== ANIMATIONS ==================== */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease-out;
        }}
        
        .slide-up {{
            animation: slideUp 0.5s ease-out;
        }}
        
        /* ==================== CUSTOM SCROLLBAR ==================== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(139, 92, 246, 0.1);
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, {THEME_COLORS['primary']}, {THEME_COLORS['accent']});
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, {THEME_COLORS['accent']}, {THEME_COLORS['primary']});
        }}
    </style>
    """, unsafe_allow_html=True)

def apply_glassmorphism():
    """Apply glassmorphism effect to main container"""
    st.markdown(f"""
    <style>
        .main .block-container {{
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(5px);
            border-radius: 30px;
            padding: 20px;
            margin: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

def apply_no_sidebar_style():
    """Apply style to hide sidebar (for landing and login pages)"""
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        
        [data-testid="stSidebarNav"] {
            display: none;
        }
        
        .stApp {
            margin-left: 0;
        }
    </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    """Show sidebar after login"""
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: block; }
    </style>
    """, unsafe_allow_html=True)

def hide_sidebar():
    """Hide sidebar for landing and login pages"""
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

def apply_landing_page_style():
    """Apply special styling for landing page"""
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(135deg, {THEME_COLORS['background_start']}, {THEME_COLORS['background_end']});
        }}
        
        .landing-hero {{
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(249, 115, 22, 0.1));
            border-radius: 40px;
            margin: 20px;
        }}
        
        .landing-title {{
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, {THEME_COLORS['primary']}, {THEME_COLORS['accent']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        
        .landing-subtitle {{
            font-size: 1.2rem;
            color: {THEME_COLORS['dark']};
            opacity: 0.8;
            max-width: 600px;
            margin: 0 auto;
        }}
    </style>
    """, unsafe_allow_html=True)

def apply_login_page_style():
    """Apply special styling for login page"""
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(rgba(10, 31, 68, 0.85), rgba(26, 58, 110, 0.85)), 
                        url('https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=2073&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        .login-card {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            border-radius: 40px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            max-width: 450px;
            margin: 60px auto;
            transition: all 0.4s ease;
        }}
        
        .login-card:hover {{
            transform: translateY(-8px);
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 35px 60px rgba(0, 0, 0, 0.4);
        }}
        
        .login-title {{
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FFFFFF, {THEME_COLORS['accent']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }}
        
        .login-subtitle {{
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 30px;
        }}
    </style>
    """, unsafe_allow_html=True)

def get_theme_colors():
    """Return the theme colors dictionary"""
    return THEME_COLORS.copy()

def get_glass_card_css():
    """Return glass card CSS as string"""
    return GLASS_CARD_STYLE

def get_button_css():
    """Return button CSS as string"""
    return BUTTON_STYLE

# ==================== MAIN EXPORTS ====================
__all__ = [
    'apply_custom_styles',
    'apply_fullscreen_styles',
    'apply_glassmorphism',
    'apply_no_sidebar_style',
    'apply_landing_page_style',
    'apply_login_page_style',
    'show_sidebar',
    'hide_sidebar',
    'get_theme_colors',
    'get_glass_card_css',
    'get_button_css',
    'THEME_COLORS',
    'GLASS_CARD_STYLE',
    'BUTTON_STYLE'
]

if __name__ == "__main__":
    print("=" * 60)
    print("🎨 STYLES MODULE TEST")
    print("=" * 60)
    print(f"\n✅ Theme colors: {THEME_COLORS['primary']}, {THEME_COLORS['accent']}")
    print("✅ Styles module ready!")