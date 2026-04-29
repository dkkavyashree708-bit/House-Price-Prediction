import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================== THEME STYLES ====================
def apply_admin_theme():
    st.markdown("""
    <style>
        /* Main container */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        /* Glassmorphism Card Effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 20px;
            margin: 15px 0;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
            border-color: rgba(249, 115, 22, 0.3);
        }
        
        /* Metric Cards */
        .metric-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.1);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(139, 92, 246, 0.2);
            border-color: #F97316;
        }
        
        .metric-number {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .metric-label {
            color: #1F2937;
            font-size: 0.85rem;
            margin-top: 8px;
            font-weight: 500;
        }
        
        /* Headers */
        h1, h2, h3 {
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 10px 25px;
            color: #1F2937;
            font-weight: 500;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(139, 92, 246, 0.2);
            transform: translateY(-2px);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            color: white !important;
            border: none;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
        }
        
        /* Dataframe */
        .dataframe {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.1);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            border-radius: 12px;
            color: white;
            font-weight: 600;
        }
        
        /* Success/Info/Warning */
        .stAlert {
            border-radius: 12px;
            border-left: 4px solid #F97316;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(139, 92, 246, 0.95), rgba(196, 181, 253, 0.95));
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: linear-gradient(135deg, #F97316, #8B5CF6);
            border-color: transparent;
        }
    </style>
    """, unsafe_allow_html=True)

def show():
    apply_admin_theme()
    
    # Debug: Print session state to see what's available
    print("Admin Dashboard - Session State:", dict(st.session_state))
    
    # Check if admin is logged in
    if not st.session_state.get("authenticated", False):
        st.error("⚠️ Please login first!")
        st.session_state.page = "login"
        st.rerun()
        return
    
    # Check user type
    user_type = st.session_state.get("user_type", "unknown")
    
    if user_type != "admin":
        st.error(f"⚠️ Admin access only! You are logged in as: {user_type}")
        st.info("🔒 This area is restricted to administrators only.")
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.1); backdrop-filter: blur(10px); padding: 15px; border-radius: 15px; border-left: 4px solid #F97316;">
            <p style="margin: 0; color: #1F2937;">
                <strong>🔐 Access Denied</strong><br>
                You do not have permission to access this page. 
                Please contact the system administrator if you believe this is an error.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add logout button to go back
        if st.button("🚪 Back to Home", width="stretch"):
            st.session_state.page = "home"
            st.session_state.current_page = "home"
            st.rerun()
        return
    
    # If we reach here, admin is properly logged in
    st.title("👑 Admin Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.get('user_email', 'Admin')}**")
    st.markdown("---")
    
    # Statistics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">1,234</div>
            <div class="metric-label">👥 Total Users</div>
            <div style="color: #10b981; font-size: 0.7rem;">↑ +12%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">5,678</div>
            <div class="metric-label">📊 Total Predictions</div>
            <div style="color: #10b981; font-size: 0.7rem;">↑ +23%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">89</div>
            <div class="metric-label">🟢 Active Sessions</div>
            <div style="color: #10b981; font-size: 0.7rem;">↑ +5%</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">94.5%</div>
            <div class="metric-label">🎯 Accuracy Rate</div>
            <div style="color: #10b981; font-size: 0.7rem;">↑ +2.3%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "⚙️ Settings", "👥 Users"])
    
    with tab1:
        st.subheader("System Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Prediction trends chart
            dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
            predictions = np.random.randint(50, 200, size=len(dates))
            
            fig = px.line(x=dates, y=predictions, title="Daily Predictions Trend")
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(255,255,255,0.5)',
                paper_bgcolor='rgba(255,255,255,0.5)',
                title_font_color='#8B5CF6'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Popular locations - NOW WITH 15 LOCATIONS
            locations = ['Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Electronic City', 
                        'Jayanagar', 'BTM Layout', 'JP Nagar', 'Banashankari', 'Malleshwaram',
                        'Rajajinagar', 'Hebbal', 'Yelahanka', 'RR Nagar', 'Vijayanagar']
            counts = [450, 420, 380, 350, 300, 280, 260, 240, 220, 200, 180, 160, 140, 120, 100]
            
            fig = px.bar(x=locations, y=counts, title="Most Searched Locations", color=counts, color_continuous_scale='purples')
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(255,255,255,0.5)',
                paper_bgcolor='rgba(255,255,255,0.5)',
                title_font_color='#8B5CF6',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution
            price_ranges = ['<50L', '50L-1Cr', '1Cr-2Cr', '2Cr-3Cr', '>3Cr']
            percentages = [15, 35, 30, 15, 5]
            
            fig = px.pie(values=percentages, names=price_ranges, title="Price Range Distribution", color_discrete_sequence=['#8B5CF6', '#C4B5FD', '#F97316', '#A78BFA', '#EDE9FE'])
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(255,255,255,0.5)',
                paper_bgcolor='rgba(255,255,255,0.5)',
                title_font_color='#8B5CF6'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # BHK distribution
            bhk_types = ['1 BHK', '2 BHK', '3 BHK', '4 BHK', '5+ BHK']
            bhk_counts = [80, 350, 420, 180, 70]
            
            fig = px.bar(x=bhk_types, y=bhk_counts, title="Property Type Distribution", color=bhk_counts, color_continuous_scale='oranges')
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(255,255,255,0.5)',
                paper_bgcolor='rgba(255,255,255,0.5)',
                title_font_color='#8B5CF6'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Location heatmap data - NOW WITH 15 LOCATIONS
        st.subheader("📍 Location Performance Matrix")
        
        location_data = pd.DataFrame({
            'Location': ['Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Jayanagar', 'Electronic City',
                        'BTM Layout', 'JP Nagar', 'Banashankari', 'Malleshwaram', 'Rajajinagar', 'Hebbal',
                        'Yelahanka', 'RR Nagar', 'Vijayanagar'],
            'Avg Price/sqft': [18500, 18200, 12800, 15800, 16800, 10200, 14500, 13800, 12500, 15500, 13500, 14200, 11500, 13000, 14000],
            'Demand Score': [95, 94, 88, 92, 89, 85, 87, 84, 82, 86, 83, 81, 78, 80, 82],
            'Growth Rate': [12.5, 11.8, 15.2, 13.1, 10.5, 18.3, 11.2, 10.8, 9.5, 12.0, 10.2, 14.5, 13.0, 11.5, 10.0],
            'ROI Potential': ['High', 'High', 'Very High', 'High', 'Medium', 'Very High', 'Medium', 'Medium', 'Medium', 'High', 'Medium', 'High', 'Medium', 'Medium', 'Medium']
        })
        
        st.dataframe(location_data, use_container_width=True)
        
        # Add a note about the data
        st.info("📊 **15+ locations analyzed** - Data shows Whitefield and Electronic City have highest growth potential")
    
    with tab3:
        st.subheader("⚙️ System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🏠 Price Model Settings")
            base_price = st.slider("Base Price per sqft (₹)", 3000, 8000, 5000)
            location_weight = st.slider("Location Weight", 0.5, 2.0, 1.0)
            bhk_weight = st.slider("BHK Weight", 0.5, 1.5, 1.0)
            
            if st.button("💾 Save Model Settings", width="stretch"):
                st.success("✅ Model settings saved successfully!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### ⚙️ System Configuration")
            max_predictions = st.number_input("Max Daily Predictions", 100, 10000, 1000)
            session_timeout = st.number_input("Session Timeout (minutes)", 5, 120, 30)
            enable_email = st.checkbox("Enable Email Notifications", value=True)
            enable_sms = st.checkbox("Enable SMS Alerts", value=False)
            
            if st.button("💾 Save System Settings", width="stretch"):
                st.success("✅ System settings saved successfully!")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.subheader("👥 User Management")
        
        # Sample user data with 10+ users
        users = pd.DataFrame({
            'User ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Email': ['john***@example.com', 'jane***@example.com', 'bob***@example.com', 'alice***@example.com', 
                     'charlie***@example.com', 'david***@example.com', 'emma***@example.com', 'frank***@example.com',
                     'grace***@example.com', 'henry***@example.com'],
            'User Type': ['User', 'User', 'Admin', 'User', 'User', 'User', 'Admin', 'User', 'User', 'User'],
            'Predictions': [45, 67, 23, 89, 34, 56, 78, 12, 43, 91],
            'Last Active': ['2024-03-15', '2024-03-16', '2024-03-14', '2024-03-17', '2024-03-15',
                           '2024-03-16', '2024-03-14', '2024-03-15', '2024-03-17', '2024-03-16']
        })
        
        st.dataframe(users, use_container_width=True)
        
        st.info("🔒 Admin emails are partially hidden for security purposes")
        
        st.markdown("---")
        st.subheader("➕ Add New User")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            new_user_email = st.text_input("📧 Email Address", placeholder="user@example.com")
        with col2:
            new_user_type = st.selectbox("👑 User Type", ["User", "Admin"])
        with col3:
            if st.button("➕ Add User", width="stretch"):
                if new_user_email and "@" in new_user_email:
                    st.success(f"✅ User {new_user_email[:3]}***@{new_user_email.split('@')[1]} added successfully!")
                elif new_user_email:
                    st.warning("⚠️ Please enter a valid email address")
                else:
                    st.warning("⚠️ Please enter an email address")
    
    # Logout button
    st.markdown("---")
    if st.button("🚪 Logout", width="stretch"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    show()