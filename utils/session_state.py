import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import hashlib

# ==================== DEFAULT VALUES ====================
DEFAULT_SESSION_STATE = {
    # Authentication
    "authenticated": False,
    "user_type": None,
    "user_email": None,
    "page": "landing",
    "show_signup": False,
    
    # Navigation
    "current_page": "home",
    "previous_page": None,
    
    # Property Data
    "predicted_price": None,
    "selected_location": None,
    "selected_features": {},
    "advanced_options": {
        'possession_status': 'Ready to Move',
        'power_backup': 'No',
        'waste_disposal': 'No',
        'water_supply': 'No',
        'maintenance_charge': 2000,
        'parking': 'None'
    },
    
    # Prediction Results
    "prediction_result": None,
    "last_prediction": None,
    
    # History (max 50 records)
    "prediction_history": [],
    "search_history": [],
    "view_history": [],
    
    # Saved/Favorite Properties (max 50)
    "saved_properties": [],
    "favorite_locations": [],
    
    # Comparison
    "compare_properties": [],
    
    # User Preferences
    "user_preferences": {
        "preferred_bhk": None,
        "preferred_budget": None,
        "preferred_locations": [],
        "preferred_area_type": None,
        "preferred_furnishing": None
    },
    
    # Analytics
    "session_start_time": None,
    "predictions_count": 0,
    "views_count": 0,
    "searches_count": 0,
    
    # Model Cache
    "model_loaded": False,
    "model": None,
    "preprocessor": None,
    "feature_cols": None,
    
    # Filters
    "filters": {
        "min_price": None,
        "max_price": None,
        "min_bhk": None,
        "max_bhk": None,
        "locations": [],
        "area_types": []
    },
    
    # UI State
    "sidebar_collapsed": False,
    "theme": "light",
    "notifications": [],
    
    # Quotes
    "daily_quote": None,
    "last_quote_date": None,
    
    # Location Map
    "selected_map_location": None,
    "map_center": [12.9716, 77.5946],
    "map_zoom": 11
}
def initialize_session_state():
    """Initialize all session state variables (alias for init_session_state)"""
    init_session_state()
# ==================== SESSION STATE INITIALIZATION ====================
def init_session_state():
    """Initialize all session state variables with default values"""
    
    for key, default_value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Set session start time if not set
    if st.session_state.session_start_time is None:
        st.session_state.session_start_time = datetime.now().isoformat()
    
    # Initialize prediction result if not exists
    if 'prediction_result' not in st.session_state:
        st.session_state.prediction_result = None

def reset_session_state():
    """Reset all session state to default values"""
    for key, default_value in DEFAULT_SESSION_STATE.items():
        st.session_state[key] = default_value
    st.session_state.session_start_time = datetime.now().isoformat()

def clear_session():
    """Clear all session state (logout)"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()

def update_session(**kwargs):
    """Update multiple session state variables at once"""
    for key, value in kwargs.items():
        st.session_state[key] = value

# ==================== PREDICTION HISTORY ====================
def save_prediction_to_history(location: str, bhk: int, sqft: float, price: float, features: Dict = None):
    """Save prediction to history with detailed information"""
    
    prediction_record = {
        "id": hashlib.md5(f"{datetime.now()}{location}{bhk}".encode()).hexdigest()[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "location": location,
        "bhk": bhk,
        "sqft": sqft,
        "price": price,
        "price_per_sqft": round(price / sqft, 2) if sqft > 0 else 0,
        "features": features or {},
        "saved": False
    }
    
    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []
    
    # Insert at beginning (most recent first)
    st.session_state.prediction_history.insert(0, prediction_record)
    
    # Keep only last 50 predictions
    if len(st.session_state.prediction_history) > 50:
        st.session_state.prediction_history = st.session_state.prediction_history[:50]
    
    # Update analytics
    st.session_state.predictions_count += 1
    
    return prediction_record["id"]

def get_prediction_history(limit: int = 10) -> List[Dict]:
    """Get prediction history with limit"""
    if "prediction_history" not in st.session_state:
        return []
    return st.session_state.prediction_history[:limit]

def get_prediction_by_id(prediction_id: str) -> Optional[Dict]:
    """Get specific prediction by ID"""
    if "prediction_history" not in st.session_state:
        return None
    
    for pred in st.session_state.prediction_history:
        if pred.get("id") == prediction_id:
            return pred
    return None

def delete_prediction(prediction_id: str) -> bool:
    """Delete a prediction from history"""
    if "prediction_history" not in st.session_state:
        return False
    
    initial_length = len(st.session_state.prediction_history)
    st.session_state.prediction_history = [
        p for p in st.session_state.prediction_history 
        if p.get("id") != prediction_id
    ]
    
    return len(st.session_state.prediction_history) < initial_length

def clear_prediction_history():
    """Clear all prediction history"""
    st.session_state.prediction_history = []

# ==================== SAVED PROPERTIES ====================
def save_property(property_data: Dict) -> bool:
    """Save property to favorites"""
    if "saved_properties" not in st.session_state:
        st.session_state.saved_properties = []
    
    # Check if already saved (by location and price)
    is_duplicate = any(
        p.get("location") == property_data.get("location") and 
        p.get("price") == property_data.get("price")
        for p in st.session_state.saved_properties
    )
    
    if not is_duplicate:
        property_with_id = {
            **property_data,
            "id": hashlib.md5(f"{datetime.now()}{property_data.get('location')}".encode()).hexdigest()[:8],
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.saved_properties.insert(0, property_with_id)
        
        # Keep only last 50 saved properties
        if len(st.session_state.saved_properties) > 50:
            st.session_state.saved_properties = st.session_state.saved_properties[:50]
        
        return True
    return False

def remove_saved_property(index: int) -> bool:
    """Remove property from saved list by index"""
    if "saved_properties" in st.session_state and index < len(st.session_state.saved_properties):
        st.session_state.saved_properties.pop(index)
        return True
    return False

def remove_saved_property_by_id(property_id: str) -> bool:
    """Remove property from saved list by ID"""
    if "saved_properties" not in st.session_state:
        return False
    
    initial_length = len(st.session_state.saved_properties)
    st.session_state.saved_properties = [
        p for p in st.session_state.saved_properties 
        if p.get("id") != property_id
    ]
    
    return len(st.session_state.saved_properties) < initial_length

def get_saved_properties() -> List[Dict]:
    """Get all saved properties"""
    if "saved_properties" not in st.session_state:
        return []
    return st.session_state.saved_properties

def is_property_saved(location: str, price: float) -> bool:
    """Check if a property is already saved"""
    if "saved_properties" not in st.session_state:
        return False
    
    return any(
        p.get("location") == location and p.get("price") == price
        for p in st.session_state.saved_properties
    )

# ==================== SEARCH HISTORY ====================
def add_to_search_history(query: str, result_count: int = 0):
    """Add search query to history"""
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    
    search_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "result_count": result_count
    }
    
    st.session_state.search_history.insert(0, search_record)
    
    # Keep only last 30 searches
    if len(st.session_state.search_history) > 30:
        st.session_state.search_history = st.session_state.search_history[:30]
    
    st.session_state.searches_count += 1

def get_search_history(limit: int = 10) -> List[Dict]:
    """Get search history"""
    if "search_history" not in st.session_state:
        return []
    return st.session_state.search_history[:limit]

# ==================== VIEW HISTORY ====================
def add_to_view_history(property_data: Dict):
    """Add property view to history"""
    if "view_history" not in st.session_state:
        st.session_state.view_history = []
    
    view_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "property": property_data
    }
    
    st.session_state.view_history.insert(0, view_record)
    
    # Keep only last 50 views
    if len(st.session_state.view_history) > 50:
        st.session_state.view_history = st.session_state.view_history[:50]
    
    st.session_state.views_count += 1

def get_view_history(limit: int = 10) -> List[Dict]:
    """Get view history"""
    if "view_history" not in st.session_state:
        return []
    return st.session_state.view_history[:limit]

# ==================== COMPARISON PROPERTIES ====================
def add_to_compare(property_data: Dict) -> bool:
    """Add property to comparison list (max 4)"""
    if "compare_properties" not in st.session_state:
        st.session_state.compare_properties = []
    
    if len(st.session_state.compare_properties) >= 4:
        return False
    
    # Check if already in comparison
    is_duplicate = any(
        p.get("location") == property_data.get("location") and 
        p.get("price") == property_data.get("price")
        for p in st.session_state.compare_properties
    )
    
    if not is_duplicate:
        st.session_state.compare_properties.append(property_data)
        return True
    return False

def remove_from_compare(index: int) -> bool:
    """Remove property from comparison list"""
    if "compare_properties" in st.session_state and index < len(st.session_state.compare_properties):
        st.session_state.compare_properties.pop(index)
        return True
    return False

def clear_compare():
    """Clear all comparison properties"""
    st.session_state.compare_properties = []

def get_compare_properties() -> List[Dict]:
    """Get comparison properties"""
    if "compare_properties" not in st.session_state:
        return []
    return st.session_state.compare_properties

# ==================== USER PREFERENCES ====================
def update_user_preferences(preferences: Dict):
    """Update user preferences"""
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = DEFAULT_SESSION_STATE["user_preferences"]
    
    for key, value in preferences.items():
        if key in st.session_state.user_preferences:
            st.session_state.user_preferences[key] = value

def get_user_preferences() -> Dict:
    """Get user preferences"""
    if "user_preferences" not in st.session_state:
        return DEFAULT_SESSION_STATE["user_preferences"]
    return st.session_state.user_preferences

# ==================== FAVORITE LOCATIONS ====================
def add_favorite_location(location: str):
    """Add location to favorites"""
    if "favorite_locations" not in st.session_state:
        st.session_state.favorite_locations = []
    
    if location not in st.session_state.favorite_locations:
        st.session_state.favorite_locations.append(location)

def remove_favorite_location(location: str):
    """Remove location from favorites"""
    if "favorite_locations" in st.session_state:
        if location in st.session_state.favorite_locations:
            st.session_state.favorite_locations.remove(location)

def get_favorite_locations() -> List[str]:
    """Get favorite locations"""
    if "favorite_locations" not in st.session_state:
        return []
    return st.session_state.favorite_locations

# ==================== FILTERS ====================
def update_filters(filters: Dict):
    """Update filter settings"""
    if "filters" not in st.session_state:
        st.session_state.filters = DEFAULT_SESSION_STATE["filters"]
    
    for key, value in filters.items():
        if key in st.session_state.filters:
            st.session_state.filters[key] = value

def get_filters() -> Dict:
    """Get current filters"""
    if "filters" not in st.session_state:
        return DEFAULT_SESSION_STATE["filters"]
    return st.session_state.filters

def clear_filters():
    """Reset all filters to default"""
    st.session_state.filters = DEFAULT_SESSION_STATE["filters"]

# ==================== NOTIFICATIONS ====================
def add_notification(message: str, type: str = "info"):
    """Add a notification message"""
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    
    notification = {
        "id": hashlib.md5(f"{datetime.now()}{message}".encode()).hexdigest()[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "type": type,
        "read": False
    }
    
    st.session_state.notifications.insert(0, notification)
    
    # Keep only last 20 notifications
    if len(st.session_state.notifications) > 20:
        st.session_state.notifications = st.session_state.notifications[:20]

def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    if "notifications" in st.session_state:
        for notif in st.session_state.notifications:
            if notif.get("id") == notification_id:
                notif["read"] = True
                break

def get_unread_notifications() -> List[Dict]:
    """Get unread notifications"""
    if "notifications" not in st.session_state:
        return []
    return [n for n in st.session_state.notifications if not n.get("read", False)]

# ==================== ANALYTICS ====================
def get_session_stats() -> Dict:
    """Get session statistics"""
    return {
        "session_duration": _get_session_duration(),
        "predictions_count": st.session_state.get("predictions_count", 0),
        "views_count": st.session_state.get("views_count", 0),
        "searches_count": st.session_state.get("searches_count", 0),
        "saved_properties_count": len(st.session_state.get("saved_properties", [])),
        "session_start": st.session_state.get("session_start_time"),
        "favorite_locations_count": len(st.session_state.get("favorite_locations", []))
    }

def _get_session_duration() -> str:
    """Calculate session duration"""
    start_time = st.session_state.get("session_start_time")
    if start_time:
        start = datetime.fromisoformat(start_time)
        duration = datetime.now() - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    return "N/A"

# ==================== MAP STATE ====================
def set_map_location(location: str, lat: float, lon: float, zoom: int = 14):
    """Set map center to a specific location"""
    st.session_state.selected_map_location = location
    st.session_state.map_center = [lat, lon]
    st.session_state.map_zoom = zoom

def get_map_state() -> Dict:
    """Get current map state"""
    return {
        "center": st.session_state.get("map_center", [12.9716, 77.5946]),
        "zoom": st.session_state.get("map_zoom", 11),
        "selected_location": st.session_state.get("selected_map_location")
    }

# ==================== MAIN EXPORTS ====================
__all__ = [
    'init_session_state',
    'reset_session_state',
    'clear_session',
    'save_prediction_to_history',
    'get_prediction_history',
    'get_prediction_by_id',
    'delete_prediction',
    'clear_prediction_history',
    'save_property',
    'remove_saved_property',
    'remove_saved_property_by_id',
    'get_saved_properties',
    'is_property_saved',
    'add_to_search_history',
    'get_search_history',
    'add_to_view_history',
    'get_view_history',
    'add_to_compare',
    'remove_from_compare',
    'clear_compare',
    'get_compare_properties',
    'update_user_preferences',
    'get_user_preferences',
    'add_favorite_location',
    'remove_favorite_location',
    'get_favorite_locations',
    'update_filters',
    'get_filters',
    'clear_filters',
    'add_notification',
    'mark_notification_read',
    'get_unread_notifications',
    'get_session_stats',
    'set_map_location',
    'get_map_state',
    'DEFAULT_SESSION_STATE'
]

if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("📦 SESSION STATE MODULE TEST")
    print("=" * 60)
    
    print("\n✅ Session state module ready!")