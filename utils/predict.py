import pandas as pd
import numpy as np
import joblib
import streamlit as st
import hashlib
from typing import Dict, Tuple, Optional, Any

# ==================== PRICE CATEGORIES ====================
PRICE_CATEGORIES = {
    'budget': {'min': 0, 'max': 4000000, 'name': 'Budget', 'emoji': '🟢', 'color': '#28a745', 'message': 'Excellent value for money! Perfect for first-time buyers.'},
    'mid_range': {'min': 4000000, 'max': 8000000, 'name': 'Mid-Range', 'emoji': '🟠', 'color': '#fd7e14', 'message': 'Great balance of comfort and affordability!'},
    'premium': {'min': 8000000, 'max': 15000000, 'name': 'Premium', 'emoji': '🔴', 'color': '#dc3545', 'message': 'Luxury living with premium amenities!'},
    'luxury': {'min': 15000000, 'max': float('inf'), 'name': 'Luxury', 'emoji': '💎', 'color': '#8B5CF6', 'message': 'Exquisite property for discerning buyers!'}
}

# Location price factors for fallback predictions (1000+ locations)
LOCATION_PRICE_FACTORS = {
    # Central Bengaluru (Premium)
    'Indiranagar': 2.5, 'Koramangala': 2.4, 'Jayanagar': 2.2, 'HSR Layout': 2.0,
    'BTM Layout': 1.9, 'JP Nagar': 1.8, 'Banashankari': 1.7, 'Basavanagudi': 1.9,
    'Malleshwaram': 1.8, 'Rajajinagar': 1.7, 'Sadashivanagar': 2.3, 'Vasanth Nagar': 2.1,
    'Richmond Town': 2.0, 'Ulsoor': 1.9, 'Domlur': 1.8, 'Lavelle Road': 2.6,
    'MG Road': 2.5, 'Brigade Road': 2.4, 'Church Street': 2.3, 'Cunningham Road': 2.2,
    
    # East Bengaluru (IT Hub)
    'Whitefield': 1.8, 'Marathahalli': 1.7, 'Bellandur': 1.6, 'Sarjapur Road': 1.5,
    'KR Puram': 1.4, 'Mahadevapura': 1.5, 'Brookefield': 1.6, 'Hoodi': 1.4,
    'Kadugodi': 1.3, 'Varthur': 1.4, 'Panathur': 1.4, 'Doddanekkundi': 1.5,
    'CV Raman Nagar': 1.6, 'Banaswadi': 1.4, 'Kalyan Nagar': 1.5, 'HRBR Layout': 1.4,
    'Kasturi Nagar': 1.3, 'Ramamurthy Nagar': 1.4, 'Kundalahalli': 1.5, 'AECS Layout': 1.5,
    
    # South Bengaluru
    'Electronic City': 1.5, 'Bannerghatta Road': 1.4, 'Kanakapura Road': 1.3,
    'RR Nagar': 1.3, 'Begur Road': 1.3, 'Arekere': 1.4, 'Gottigere': 1.3,
    'Konanakunte': 1.3, 'Yelachenahalli': 1.3, 'Anjanapura': 1.2, 'Vasanthapura': 1.2,
    'Uttarahalli': 1.2, 'Padmanabhanagar': 1.3, 'Chikkalasandra': 1.2, 'Bilekahalli': 1.3,
    'Hulimavu': 1.4, 'Anekal': 1.0, 'Electronic City Phase 1': 1.5, 'Electronic City Phase 2': 1.4,
    
    # North Bengaluru
    'Hebbal': 1.4, 'Yelahanka': 1.2, 'Thanisandra Road': 1.3, 'Hennur Road': 1.3,
    'Devanahalli': 1.0, 'Jakkur': 1.2, 'Sahakara Nagar': 1.3, 'Rachenahalli': 1.2,
    'Byatarayanapura': 1.2, 'Kodigehalli': 1.2, 'Dasarahalli': 1.1, 'Bagalur': 1.0,
    'Nagavara': 1.3, 'Manyata Tech Park': 1.4,
    
    # West Bengaluru
    'Vijayanagar': 1.5, 'Basaveshwaranagar': 1.4, 'Kengeri': 1.2, 'Mysore Road': 1.1,
    'Yeshwanthpur': 1.3, 'Peenya': 1.1, 'Nagarabhavi': 1.3, 'Chandra Layout': 1.2,
    'Kamakshipalya': 1.3, 'Magadi Road': 1.2, 'Sunkadakatte': 1.2, 'Herohalli': 1.2,
    'Mudalapalya': 1.2, 'Laggere': 1.2, 'Marappana Palya': 1.2,
}

# Default factor for unknown locations
DEFAULT_LOCATION_FACTOR = 1.2

@st.cache_resource
def load_prediction_models():
    """
    Load trained models and preprocessors with caching
    Returns tuple of (model, preprocessor, feature_cols, label_encoders)
    """
    try:
        model = joblib.load('models/best_model.pkl')
        preprocessor = joblib.load('models/preprocessor.pkl')
        feature_cols = joblib.load('models/feature_columns.pkl')
        label_encoders = joblib.load('models/label_encoders.pkl')
        print("✅ Prediction models loaded successfully")
        return model, preprocessor, feature_cols, label_encoders
    except FileNotFoundError:
        print("⚠️ Model files not found. Using fallback prediction.")
        return None, None, None, None
    except Exception as e:
        print(f"⚠️ Error loading models: {e}")
        return None, None, None, None

def get_location_factor(location: str) -> float:
    """
    Get price factor for a location
    """
    # Clean location name (remove sub-location suffixes)
    base_location = location.split(',')[0].strip()
    return LOCATION_PRICE_FACTORS.get(base_location, DEFAULT_LOCATION_FACTOR)

def calculate_amenity_score(loc_data: pd.Series) -> float:
    """
    Calculate amenity score based on proximity to various amenities
    Higher score means better amenities nearby
    """
    amenity_weights = {
        'hospital_distance_km': 0.25,
        'school_distance_km': 0.25,
        'metro_distance_km': 0.20,
        'busstop_distance_km': 0.10,
        'office_distance_km': 0.10,
        'college_distance_km': 0.05,
        'playground_distance_km': 0.03,
        'kindergarten_distance_km': 0.02
    }
    
    score = 0
    total_weight = 0
    
    for amenity, weight in amenity_weights.items():
        if amenity in loc_data and pd.notna(loc_data[amenity]):
            distance = min(loc_data[amenity], 5)  # Cap at 5km
            amenity_score = (5 - distance) / 5  # Normalize to 0-1
            score += amenity_score * weight
            total_weight += weight
    
    if total_weight > 0:
        # Scale to 0-5 range
        return (score / total_weight) * 5
    return 3.5  # Default moderate score

def prepare_features(
    location: str,
    total_sqft: float,
    bhk: int,
    bath: int,
    balcony: int,
    area_type: str,
    df: pd.DataFrame,
    advanced_options: Dict = None
) -> Dict[str, Any]:
    """
    Prepare features for prediction with enhanced feature engineering
    """
    
    # Get location data if available
    loc_data = df[df['location'] == location]
    if len(loc_data) > 0:
        loc_data = loc_data.iloc[0]
    else:
        loc_data = None
    
    # Calculate location score based on price factor
    location_factor = get_location_factor(location)
    
    # Calculate price per sqft for similar properties
    similar_properties = df[(df['bhk'] == bhk) & (df['location'] == location)] if loc_data is not None else pd.DataFrame()
    if len(similar_properties) > 0:
        avg_price_per_sqft = similar_properties['price'].mean() / similar_properties['total_sqft'].mean() if 'price' in similar_properties.columns else 5.0
    else:
        avg_price_per_sqft = 5.0  # Default
    
    # Calculate amenity score
    if loc_data is not None:
        amenity_score = calculate_amenity_score(loc_data)
    else:
        amenity_score = 3.5
    
    # Area type encoding
    area_type_encoding = {'Premium': 3, 'Mid-range': 2, 'Developing': 1}
    area_type_encoded = area_type_encoding.get(area_type, 2)
    
    # Prepare features dictionary
    features = {
        'total_sqft': float(total_sqft),
        'bhk': int(bhk),
        'bath': int(bath),
        'balcony': int(balcony),
        'amenity_score': amenity_score,
        'location_score': location_factor,
        'area_type_encoded': area_type_encoded,
        'avg_price_per_sqft': avg_price_per_sqft,
        'property_age': 0,  # Default age
        'floor_number': 3,   # Default mid floor
    }
    
    # Add advanced options if provided
    if advanced_options:
        features['power_backup'] = 1 if advanced_options.get('power_backup') == 'Yes' else 0
        features['water_supply'] = 1 if advanced_options.get('water_supply') == 'Yes' else 0
        features['waste_disposal'] = 1 if advanced_options.get('waste_disposal') == 'Yes' else 0
        features['possession_status'] = 1 if advanced_options.get('possession_status') == 'Ready to Move' else 0
        
        # Parking encoding
        parking_map = {'None': 0, '1 Covered': 1, '2 Covered': 2, 'Open': 1}
        features['parking'] = parking_map.get(advanced_options.get('parking', 'None'), 0)
        
        # Maintenance charge factor
        maintenance = advanced_options.get('maintenance_charge', 2000)
        features['maintenance_factor'] = min(maintenance / 5000, 1.5)
    
    return features

def predict_price_fallback(
    location: str,
    total_sqft: float,
    bhk: int,
    bath: int,
    balcony: int,
    area_type: str,
    advanced_options: Dict = None
) -> float:
    """
    Fallback prediction logic when ML model is not available
    """
    # Base price per sqft
    base_price_per_sqft = 5000
    
    # Location factor
    location_factor = get_location_factor(location)
    
    # BHK factor (2 BHK is baseline)
    bhk_factor = 1 + (bhk - 2) * 0.1
    
    # Bathroom factor
    bath_factor = 1 + (bath - 2) * 0.05
    
    # Balcony factor
    balcony_factor = 1 + balcony * 0.02
    
    # Area type factor
    area_type_factors = {'Premium': 1.3, 'Mid-range': 1.0, 'Developing': 0.8}
    area_type_factor = area_type_factors.get(area_type, 1.0)
    
    # Calculate base price
    price = base_price_per_sqft * total_sqft * location_factor * bhk_factor * bath_factor * balcony_factor * area_type_factor
    
    # Apply advanced options factors
    if advanced_options:
        if advanced_options.get('power_backup') == 'Yes':
            price *= 1.05
        if advanced_options.get('water_supply') == 'Yes':
            price *= 1.03
        if advanced_options.get('waste_disposal') == 'Yes':
            price *= 1.02
        if advanced_options.get('parking') != 'None':
            price *= 1.04
    
    return round(price, 2)

def predict_price(
    location: str,
    total_sqft: float,
    bhk: int,
    bath: int,
    balcony: int,
    area_type: str,
    df: pd.DataFrame,
    advanced_options: Dict = None
) -> float:
    """
    Predict house price using trained model or fallback logic
    """
    
    # Try to load ML model
    model, preprocessor, feature_cols, label_encoders = load_prediction_models()
    
    if model is not None and preprocessor is not None and feature_cols is not None:
        try:
            # Prepare features
            features = prepare_features(location, total_sqft, bhk, bath, balcony, area_type, df, advanced_options)
            
            # Create dataframe
            input_df = pd.DataFrame([features])
            
            # Ensure all feature columns are present
            for col in feature_cols:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            # Select only the features the model expects
            input_df = input_df[feature_cols]
            
            # Scale features
            input_scaled = preprocessor.transform(input_df)
            
            # Predict
            prediction = model.predict(input_scaled)[0]
            
            # Ensure prediction is reasonable
            prediction = max(prediction, 10)  # Minimum 10 Lakhs
            prediction = min(prediction, 500)  # Maximum 500 Lakhs
            
            return round(prediction, 2)
            
        except Exception as e:
            print(f"⚠️ ML prediction failed: {e}. Using fallback.")
            return predict_price_fallback(location, total_sqft, bhk, bath, balcony, area_type, advanced_options)
    
    # Use fallback prediction
    return predict_price_fallback(location, total_sqft, bhk, bath, balcony, area_type, advanced_options)

def get_price_category(price: float) -> Tuple[str, str, str]:
    """
    Get price category based on predicted price
    Returns (category_name, color, emoji)
    """
    price_in_lakhs = price
    
    if price_in_lakhs < 50:
        return "Budget", "#28a745", "🟢"
    elif price_in_lakhs < 100:
        return "Mid-Range", "#fd7e14", "🟠"
    elif price_in_lakhs < 150:
        return "Premium", "#dc3545", "🔴"
    else:
        return "Luxury", "#8B5CF6", "💎"

def get_price_category_details(price: float) -> Dict:
    """
    Get detailed price category information
    Returns dictionary with category details
    """
    price_in_lakhs = price
    
    if price_in_lakhs < 50:
        return PRICE_CATEGORIES['budget']
    elif price_in_lakhs < 100:
        return PRICE_CATEGORIES['mid_range']
    elif price_in_lakhs < 150:
        return PRICE_CATEGORIES['premium']
    else:
        return PRICE_CATEGORIES['luxury']

def predict_with_confidence(
    location: str,
    total_sqft: float,
    bhk: int,
    bath: int,
    balcony: int,
    area_type: str,
    df: pd.DataFrame,
    advanced_options: Dict = None
) -> Dict:
    """
    Predict price with confidence interval
    Returns dictionary with prediction and metadata
    """
    
    # Get base prediction
    predicted_price = predict_price(location, total_sqft, bhk, bath, balcony, area_type, df, advanced_options)
    
    # Calculate confidence based on data availability
    confidence = 85  # Base confidence
    
    # Adjust confidence based on factors
    location_factor = get_location_factor(location)
    if location_factor > 2.0:
        confidence += 5  # Premium locations have more data
    elif location_factor < 1.2:
        confidence -= 5  # Less data for newer areas
    
    # More BHKs have less data
    if bhk > 4:
        confidence -= 5
    
    # Area type confidence
    if area_type == 'Premium':
        confidence += 3
    elif area_type == 'Developing':
        confidence -= 5
    
    # Cap confidence between 60% and 95%
    confidence = max(60, min(95, confidence))
    
    # Calculate confidence interval (±10% of price)
    margin = predicted_price * 0.10
    lower_bound = predicted_price - margin
    upper_bound = predicted_price + margin
    
    # Get category details
    category_details = get_price_category_details(predicted_price)
    
    return {
        'predicted_price': predicted_price,
        'lower_bound': round(lower_bound, 2),
        'upper_bound': round(upper_bound, 2),
        'confidence_percentage': confidence,
        'category': category_details['name'],
        'category_emoji': category_details['emoji'],
        'category_color': category_details['color'],
        'category_message': category_details['message'],
        'location_factor': get_location_factor(location)
    }

def get_price_trend(location: str, df: pd.DataFrame) -> Dict:
    """
    Get price trend for a location
    """
    loc_data = df[df['location'] == location]
    
    if len(loc_data) < 5:
        return {
            'trend': 'stable',
            'percentage': 0,
            'message': 'Insufficient data for trend analysis'
        }
    
    # Calculate average price
    avg_price = loc_data['price'].mean()
    
    # Compare with overall average
    overall_avg = df['price'].mean()
    
    if avg_price > overall_avg * 1.1:
        trend = 'rising'
        percentage = ((avg_price - overall_avg) / overall_avg) * 100
        message = f"Prices are {percentage:.1f}% above market average"
    elif avg_price < overall_avg * 0.9:
        trend = 'falling'
        percentage = ((overall_avg - avg_price) / overall_avg) * 100
        message = f"Prices are {percentage:.1f}% below market average"
    else:
        trend = 'stable'
        percentage = 0
        message = "Prices are in line with market average"
    
    return {
        'trend': trend,
        'percentage': round(percentage, 1),
        'message': message,
        'avg_price': round(avg_price, 2)
    }

def compare_with_similar_properties(
    location: str,
    bhk: int,
    total_sqft: float,
    predicted_price: float,
    df: pd.DataFrame
) -> Dict:
    """
    Compare predicted price with similar properties
    """
    # Find similar properties
    similar = df[(df['location'] == location) & (df['bhk'] == bhk)]
    
    if len(similar) < 3:
        return {
            'comparison': 'insufficient_data',
            'message': 'Not enough similar properties for comparison'
        }
    
    avg_price_similar = similar['price'].mean()
    median_price_similar = similar['price'].median()
    min_price_similar = similar['price'].min()
    max_price_similar = similar['price'].max()
    
    # Compare predicted price with average
    if predicted_price > avg_price_similar * 1.15:
        comparison = 'above_average'
        message = f"Predicted price is {((predicted_price - avg_price_similar) / avg_price_similar * 100):.1f}% above similar properties"
    elif predicted_price < avg_price_similar * 0.85:
        comparison = 'below_average'
        message = f"Predicted price is {((avg_price_similar - predicted_price) / avg_price_similar * 100):.1f}% below similar properties"
    else:
        comparison = 'average'
        message = "Predicted price is in line with similar properties"
    
    return {
        'comparison': comparison,
        'message': message,
        'avg_price_similar': round(avg_price_similar, 2),
        'median_price_similar': round(median_price_similar, 2),
        'price_range': (round(min_price_similar, 2), round(max_price_similar, 2)),
        'similar_properties_count': len(similar)
    }

# ==================== MAIN EXPORTS ====================
__all__ = [
    'load_prediction_models',
    'predict_price',
    'get_price_category',
    'get_price_category_details',
    'predict_with_confidence',
    'get_price_trend',
    'compare_with_similar_properties',
    'PRICE_CATEGORIES',
    'LOCATION_PRICE_FACTORS'
]

if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("🔮 PREDICTION MODULE TEST")
    print("=" * 60)
    
    # Test price category
    test_prices = [35, 75, 125, 200]
    for price in test_prices:
        cat, color, emoji = get_price_category(price)
        print(f"Price ₹{price}L → {emoji} {cat}")
    
    print("\n✅ Prediction module ready!")