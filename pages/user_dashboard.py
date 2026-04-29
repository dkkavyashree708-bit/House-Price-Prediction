import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import apply_custom_styles

# Cache data loading for better performance
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv('data/Bengaluru_House_Data.csv')
        # Print column names for debugging
        print("Available columns:", df.columns.tolist())
        
        # Rename columns if needed to match expected names
        if 'BHK' in df.columns and 'bhk' not in df.columns:
            df.rename(columns={'BHK': 'bhk'}, inplace=True)
        if 'BATH' in df.columns and 'bath' not in df.columns:
            df.rename(columns={'BATH': 'bath'}, inplace=True)
        if 'BALCONY' in df.columns and 'balcony' not in df.columns:
            df.rename(columns={'BALCONY': 'balcony'}, inplace=True)
        if 'AREA_TYPE' in df.columns and 'area_type' not in df.columns:
            df.rename(columns={'AREA_TYPE': 'area_type'}, inplace=True)
        if 'TOTAL_SQFT' in df.columns and 'total_sqft' not in df.columns:
            df.rename(columns={'TOTAL_SQFT': 'total_sqft'}, inplace=True)
        if 'PRICE' in df.columns and 'price' not in df.columns:
            df.rename(columns={'PRICE': 'price'}, inplace=True)
            
        return df
    except FileNotFoundError:
        # Create sample data if file doesn't exist
        st.warning("Data file not found. Using sample data with 20+ locations.")
        return create_sample_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for testing with 20+ locations"""
    np.random.seed(42)
    
    # 20+ Bangalore locations for testing
    locations = [
        'Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Jayanagar', 
        'Electronic City', 'Hebbal', 'Yelahanka', 'BTM Layout', 'JP Nagar',
        'Banashankari', 'Malleshwaram', 'Rajajinagar', 'Vijayanagar', 'Basaveshwaranagar',
        'Marathahalli', 'Bellandur', 'Sarjapur Road', 'KR Puram', 'Mahadevapura',
        'Brookefield', 'Ulsoor', 'Richmond Town', 'Sadashivanagar', 'Frazer Town',
        'RR Nagar', 'Kengeri', 'Yeshwanthpur', 'Peenya', 'Nagarabhavi'
    ]
    
    # Coordinates for these locations (approximate)
    location_coords = {
        'Indiranagar': (12.9784, 77.6408), 'Koramangala': (12.9279, 77.6271),
        'Whitefield': (12.9698, 77.7499), 'HSR Layout': (12.9120, 77.6448),
        'Jayanagar': (12.9299, 77.5805), 'Electronic City': (12.8456, 77.6603),
        'Hebbal': (13.0359, 77.5970), 'Yelahanka': (13.1007, 77.5963),
        'BTM Layout': (12.9169, 77.6105), 'JP Nagar': (12.9066, 77.5851),
        'Banashankari': (12.9300, 77.5500), 'Malleshwaram': (13.0060, 77.5690),
        'Rajajinagar': (12.9992, 77.5557), 'Vijayanagar': (12.9570, 77.5320),
        'Basaveshwaranagar': (12.9907, 77.5311), 'Marathahalli': (12.9552, 77.7008),
        'Bellandur': (12.9258, 77.6768), 'Sarjapur Road': (12.8789, 77.7014),
        'KR Puram': (13.0058, 77.7020), 'Mahadevapura': (12.9930, 77.6867),
        'Brookefield': (12.9690, 77.7216), 'Ulsoor': (12.9797, 77.6235),
        'Richmond Town': (12.9669, 77.6063), 'Sadashivanagar': (13.0106, 77.5692),
        'Frazer Town': (12.9900, 77.6100), 'RR Nagar': (12.9089, 77.4963),
        'Kengeri': (12.9000, 77.4833), 'Yeshwanthpur': (13.0285, 77.5488),
        'Peenya': (13.0316, 77.5148), 'Nagarabhavi': (12.9500, 77.5100)
    }
    
    data = {
        'location': np.random.choice(locations, 1500),
        'total_sqft': np.random.normal(1200, 300, 1500),
        'bhk': np.random.choice([1,2,3,4,5], 1500),
        'bath': np.random.choice([1,2,3,4], 1500),
        'balcony': np.random.choice([0,1,2,3], 1500),
        'area_type': np.random.choice(['Premium', 'Mid-range', 'Developing'], 1500),
        'price': np.random.normal(100, 30, 1500),
    }
    
    df = pd.DataFrame(data)
    
    # Add coordinates
    df['latitude'] = df['location'].map(lambda x: location_coords.get(x, (12.9716, 77.5946))[0])
    df['longitude'] = df['location'].map(lambda x: location_coords.get(x, (12.9716, 77.5946))[1])
    
    # Add amenity distances
    df['school_distance_km'] = np.random.uniform(0.5, 5, 1500)
    df['hospital_distance_km'] = np.random.uniform(0.5, 5, 1500)
    df['metro_distance_km'] = np.random.uniform(0.5, 5, 1500)
    
    return df

def predict_price(location, total_sqft, bhk, bath, balcony, area_type, df):
    """Simple price prediction function"""
    try:
        # Check if required columns exist
        required_cols = ['location', 'bhk', 'price', 'total_sqft']
        for col in required_cols:
            if col not in df.columns:
                print(f"Column '{col}' not found in DataFrame")
                return 100.0
        
        # Filter similar properties
        similar = df[(df['location'] == location) & (df['bhk'] == bhk)]
        
        if len(similar) > 0:
            base_price = similar['price'].mean()
        else:
            base_price = df['price'].mean()
        
        # Adjust based on sqft
        avg_sqft = df['total_sqft'].mean()
        sqft_factor = total_sqft / avg_sqft if avg_sqft > 0 else 1.0
        
        # Area type factor
        area_factors = {'Premium': 1.3, 'Mid-range': 1.0, 'Developing': 0.8}
        
        predicted = base_price * sqft_factor * area_factors.get(area_type, 1.0)
        return round(predicted, 2)
    except Exception as e:
        print(f"Prediction error: {e}")
        return 100.0

def get_price_category(price):
    """Get price category based on predicted price"""
    if price < 50:
        return "Budget", "green", "🟢"
    elif price < 100:
        return "Mid-Range", "orange", "🟠"
    elif price < 150:
        return "Premium", "red", "🔴"
    else:
        return "Luxury", "purple", "💜"

def save_prediction_to_history(location, bhk, sqft, price):
    """Save prediction to session history"""
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    
    st.session_state.prediction_history.append({
        'location': location,
        'bhk': bhk,
        'sqft': sqft,
        'price': price,
        'timestamp': pd.Timestamp.now()
    })

# ==================== THEME STYLES ====================
def apply_user_theme():
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
        
        /* Metric Cards */
        .metric-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(139, 92, 246, 0.2);
            border-color: #F97316;
        }
        
        .metric-number {
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Headers */
        h1, h2, h3 {
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
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
        
        /* Map Container - FULL WIDTH FIX */
        .folium-map {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
            transition: all 0.3s ease;
            width: 100% !important;
            height: 450px !important;
        }
        
        .folium-map:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {
            border-radius: 12px !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
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
    </style>
    """, unsafe_allow_html=True)

def show():
    apply_user_theme()
    
    # Check authentication
    if not st.session_state.get("authenticated", False):
        st.warning("Please login first!")
        st.session_state.page = "login"
        st.rerun()
        return
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('user_email', 'Guest')}")
        st.markdown(f"### 🏷️ Role: {st.session_state.get('user_type', 'Guest').upper()}")
        st.markdown("---")
        
        if st.button("📊 Results & Insights", width="stretch"):
            st.session_state.page = "results_insights"
            st.rerun()
        
        if st.button("🏠 Home", width="stretch"):
            st.session_state.page = "landing"
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", width="stretch"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.title("🏠 SmartEstate Property Predictor")
    st.markdown(f"*📍 {df['location'].nunique()} Bangalore locations • {len(df)} properties in database*")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Property Details")
        
        with st.form("prediction_form"):
            # Get unique locations
            locations = sorted(df['location'].unique())
            location = st.selectbox("📍 Location", locations, help="Select from Bangalore locations")
            
            # Get data for selected location safely
            loc_data = df[df['location'] == location]
            
            col_a, col_b = st.columns(2)
            with col_a:
                total_sqft = st.number_input("📐 Total Sqft", min_value=300.0, max_value=10000.0,
                                             value=float(1200.0), step=50.0)
                
                # Safe BHK selection
                try:
                    if len(loc_data) > 0 and 'bhk' in loc_data.columns:
                        default_bhk = int(loc_data['bhk'].mode()[0]) if len(loc_data['bhk'].mode()) > 0 else 2
                    else:
                        default_bhk = 2
                except:
                    default_bhk = 2
                bhk = st.selectbox("🏠 BHK", [1,2,3,4,5,6], index=[1,2,3,4,5,6].index(default_bhk) if default_bhk in [1,2,3,4,5,6] else 1)
            
            with col_b:
                # Safe Bath selection
                try:
                    if len(loc_data) > 0 and 'bath' in loc_data.columns:
                        default_bath = int(loc_data['bath'].mode()[0]) if len(loc_data['bath'].mode()) > 0 else 2
                    else:
                        default_bath = 2
                except:
                    default_bath = 2
                bath = st.selectbox("🛁 Bathrooms", [1,2,3,4,5], index=[1,2,3,4,5].index(default_bath) if default_bath in [1,2,3,4,5] else 1)
                
                # Safe Balcony selection
                try:
                    if len(loc_data) > 0 and 'balcony' in loc_data.columns:
                        default_balcony = int(loc_data['balcony'].mode()[0]) if len(loc_data['balcony'].mode()) > 0 else 1
                    else:
                        default_balcony = 1
                except:
                    default_balcony = 1
                balcony = st.selectbox("🌴 Balcony", [0,1,2,3,4], index=[0,1,2,3,4].index(default_balcony) if default_balcony in [0,1,2,3,4] else 1)
            
            # Safe Area Type
            try:
                if len(loc_data) > 0 and 'area_type' in loc_data.columns:
                    default_area = loc_data['area_type'].mode()[0] if len(loc_data['area_type'].mode()) > 0 else "Mid-range"
                else:
                    default_area = "Mid-range"
            except:
                default_area = "Mid-range"
            
            area_options = ["Premium", "Mid-range", "Developing"]
            area_index = area_options.index(default_area) if default_area in area_options else 1
            area_type = st.selectbox("📏 Area Type", area_options, index=area_index)
            
            # Submit button inside form
            submitted = st.form_submit_button("🔮 Predict Price", type="primary", width="stretch")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submitted:
            # Predict price
            predicted_price = predict_price(location, total_sqft, bhk, bath, balcony, area_type, df)
            category, color, emoji = get_price_category(predicted_price)
            
            # Save to session
            st.session_state.predicted_price = predicted_price
            st.session_state.selected_location = location
            st.session_state.bhk = bhk
            st.session_state.total_sqft = total_sqft
            st.session_state.bath = bath
            st.session_state.balcony = balcony
            
            save_prediction_to_history(location, bhk, total_sqft, predicted_price)
            
            # Display results
            st.markdown("---")
            st.markdown("### 💰 Prediction Result")
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Predicted Price", f"₹{predicted_price:,.2f} Lakhs")
            with m2:
                st.markdown(f"**Category:** <span style='color:{color};font-weight:bold;font-size:1.2rem'>{emoji} {category}</span>", 
                           unsafe_allow_html=True)
            with m3:
                st.metric("Price per Sqft", f"₹{(predicted_price/total_sqft)*1000:,.2f}")
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🗺️ Location Map")
        
        if 'selected_location' in st.session_state:
            loc_data = df[df['location'] == st.session_state.selected_location]
            if len(loc_data) > 0:
                loc_data_full = loc_data.iloc[0]
                lat = loc_data_full.get('latitude', 12.9716)
                lon = loc_data_full.get('longitude', 77.5946)
                
                if 'predicted_price' in st.session_state:
                    _, _, marker_color = get_price_category(st.session_state.predicted_price)
                else:
                    marker_color = "blue"
                
                # Create map - FULL WIDTH (using width=100%)
                m = folium.Map(location=[lat, lon], zoom_start=14, control_scale=True, width='100%', height=450)
                
                popup_html = f"""
                <div style="font-family: Arial; min-width: 200px;">
                    <b>📍 {st.session_state.selected_location}</b><br>
                    <b>💰 Price:</b> ₹{st.session_state.get('predicted_price', 'N/A')} Lakhs<br>
                    <b>🏠 BHK:</b> {st.session_state.get('bhk', 'N/A')}<br>
                    <b>📐 Sqft:</b> {st.session_state.get('total_sqft', 'N/A')}<br>
                </div>
                """
                
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=marker_color, icon='home', prefix='fa')
                ).add_to(m)
                
                folium_static(m, width=1000, height=450)
            else:
                st.info("No data available for this location")
        else:
            # Show full width map of Bangalore
            m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, control_scale=True, width='100%', height=450)
            folium_static(m, width=1000, height=450)
            st.info("👈 Fill property details and click 'Predict Price' to see location map")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    show()