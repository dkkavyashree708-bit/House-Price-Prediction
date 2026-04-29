import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# DO NOT call st.set_page_config here - it's already called in app.py

# ==================== THEME STYLES ====================
def apply_insights_theme():
    st.markdown("""
    <style>
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
        
        /* Recommendation Card */
        .rec-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.1);
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .rec-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 35px rgba(139, 92, 246, 0.2);
            border-color: #F97316;
        }
        
        .rec-title {
            font-size: 1.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
        }
        
        .rec-price {
            font-size: 1.5rem;
            font-weight: 800;
            color: #F97316;
            margin: 10px 0;
        }
        
        .rec-badge {
            display: inline-block;
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 10px;
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
        
        /* Sidebar Filters */
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
        
        /* Slider */
        .stSlider > div > div > div {
            background: linear-gradient(90deg, #8B5CF6, #F97316) !important;
        }
        
        /* Multiselect */
        .stMultiSelect [data-baseweb="select"] {
            background: rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
        }
        
        /* Map Container */
        .folium-map {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
            transition: all 0.3s ease;
        }
        
        .folium-map:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
        }
    </style>
    """, unsafe_allow_html=True)

def show():
    apply_insights_theme()
    
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Please login first!")
        st.session_state.page = "login"
        st.rerun()
        return
    
    st.title("📊 Results & Insights")
    st.markdown("---")
    
    if st.button("← Back to Dashboard", width="stretch"):
        st.session_state.page = "user_dashboard"
        st.rerun()
    
    # Generate sample data
    np.random.seed(42)
    df = pd.DataFrame({
        'price': np.random.normal(100, 30, 500),
        'total_sqft': np.random.normal(1200, 300, 500),
        'bhk': np.random.choice([1,2,3,4,5], 500),
        'location': np.random.choice(['Koramangala', 'Indiranagar', 'Whitefield', 'Electronic City', 'HSR Layout'], 500)
    })
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        st.markdown("---")
        locations = st.multiselect("📍 Location", df['location'].unique(), default=df['location'].unique()[:2])
        price_range = st.slider("💰 Price Range (Lakhs)", 0, 250, (50, 150))
        bhk_filter = st.multiselect("🏠 BHK", [1,2,3,4,5], default=[2,3])
        st.markdown("---")
        st.caption("✨ Filter properties to get personalized insights")
    
    # Apply filters
    filtered_df = df
    if locations:
        filtered_df = filtered_df[filtered_df['location'].isin(locations)]
    filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]
    if bhk_filter:
        filtered_df = filtered_df[filtered_df['bhk'].isin(bhk_filter)]
    
    # Show results count
    st.info(f"📊 Showing **{len(filtered_df)}** properties matching your criteria")
    
    # Tab layout
    tab1, tab2, tab3 = st.tabs(["📈 Visualizations", "🗺️ Property Map", "💡 Recommendations"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig1 = px.histogram(filtered_df, x='price', title='Price Distribution', nbins=30, color_discrete_sequence=['#8B5CF6'])
            fig1.update_layout(plot_bgcolor='rgba(255,255,255,0.5)', paper_bgcolor='rgba(255,255,255,0.5)', title_font_color='#8B5CF6')
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            bhk_stats = filtered_df.groupby('bhk')['price'].mean().reset_index()
            fig2 = px.bar(bhk_stats, x='bhk', y='price', title='Avg Price by BHK', color='price', color_continuous_scale='purples')
            fig2.update_layout(plot_bgcolor='rgba(255,255,255,0.5)', paper_bgcolor='rgba(255,255,255,0.5)', title_font_color='#8B5CF6')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Heatmap
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        heatmap_data = filtered_df.pivot_table(values='price', index='bhk', columns='location', aggfunc='mean').fillna(0)
        fig3 = px.imshow(heatmap_data, title='Price Heatmap by Location & BHK', aspect='auto', color_continuous_scale='purples')
        fig3.update_layout(title_font_color='#8B5CF6')
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Feature importance
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Feature Importance")
        features = ['Total Sqft', 'BHK', 'Location', 'Bathrooms', 'Balcony']
        importance = [35, 28, 25, 7, 5]
        fig4 = px.bar(x=importance, y=features, orientation='h', title='What Affects Price Most?', color=importance, color_continuous_scale='oranges')
        fig4.update_layout(plot_bgcolor='rgba(255,255,255,0.5)', paper_bgcolor='rgba(255,255,255,0.5)', title_font_color='#8B5CF6')
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🗺️ Property Map with Clustering")
        
        # Create map with more locations
        location_coords = {
            'Koramangala': (12.9279, 77.6271),
            'Indiranagar': (12.9784, 77.6408),
            'Whitefield': (12.9698, 77.7499),
            'Electronic City': (12.8453, 77.6603),
            'HSR Layout': (12.9120, 77.6420),
            'Jayanagar': (12.9299, 77.5805),
            'BTM Layout': (12.9169, 77.6105),
            'JP Nagar': (12.9066, 77.5851),
            'Hebbal': (13.0359, 77.5970),
            'Yelahanka': (13.1007, 77.5963)
        }
        
        m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(m)
        
        for _, row in filtered_df.head(100).iterrows():
            lat, lon = location_coords.get(row['location'], (12.9716, 77.5946))
            color = 'green' if row['price'] < 50 else 'orange' if row['price'] <= 120 else 'red'
            folium.CircleMarker(
                location=[lat, lon], radius=8, popup=f"{row['location']}<br>₹{row['price']:.0f}L<br>{row['bhk']} BHK",
                color=color, fill=True, fill_color=color,
                fill_opacity=0.7
            ).add_to(marker_cluster)
        
        folium_static(m, width=None, height=500)
        st.caption("🟢 Budget (<50L) | 🟠 Mid-Range (50L-120L) | 🔴 Luxury (>120L)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💡 Recommended Properties For You")
        
        # More recommendations
        recommendations = [
            {"location": "Koramangala", "price": "95 Lakhs", "sqft": "1250", "bhk": "2", "label": "⭐ Best Match", "roi": "12%"},
            {"location": "Indiranagar", "price": "110 Lakhs", "sqft": "1400", "bhk": "3", "label": "💎 High Value", "roi": "15%"},
            {"location": "HSR Layout", "price": "85 Lakhs", "sqft": "1150", "bhk": "2", "label": "💰 Within Budget", "roi": "11%"},
            {"location": "Whitefield", "price": "75 Lakhs", "sqft": "1200", "bhk": "2", "label": "🚀 Fast Growth", "roi": "18%"},
            {"location": "Electronic City", "price": "65 Lakhs", "sqft": "1100", "bhk": "2", "label": "📈 High Demand", "roi": "14%"},
            {"location": "Jayanagar", "price": "120 Lakhs", "sqft": "1500", "bhk": "3", "label": "✨ Premium Pick", "roi": "10%"}
        ]
        
        cols = st.columns(3)
        for idx, rec in enumerate(recommendations[:3]):
            with cols[idx]:
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-title">🏠 {rec['location']}</div>
                    <div class="rec-price">{rec['price']}</div>
                    <p>📏 {rec['sqft']} sqft | 🛏️ {rec['bhk']} BHK</p>
                    <p>📈 Expected ROI: {rec['roi']}</p>
                    <span class="rec-badge">{rec['label']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        cols2 = st.columns(3)
        for idx, rec in enumerate(recommendations[3:6]):
            with cols2[idx]:
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-title">🏠 {rec['location']}</div>
                    <div class="rec-price">{rec['price']}</div>
                    <p>📏 {rec['sqft']} sqft | 🛏️ {rec['bhk']} BHK</p>
                    <p>📈 Expected ROI: {rec['roi']}</p>
                    <span class="rec-badge">{rec['label']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Investment Tip
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(249,115,22,0.1)); 
                    border-radius: 15px; padding: 15px; margin-top: 20px; border-left: 4px solid #F97316;">
            <strong>💡 Investment Tip:</strong> Properties in Whitefield and Electronic City are showing the highest growth 
            potential with expected appreciation of 15-18% in the next year.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()