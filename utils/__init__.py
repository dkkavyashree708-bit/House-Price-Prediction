# ============================================================================
# UTILS PACKAGE INITIALIZATION
# SmartEstate - Bangalore House Price Prediction System
# ============================================================================
# Version: 2.0.0
# Theme: Soft Purple (#8B5CF6) + Warm Orange (#F97316)
# ============================================================================

"""
SmartEstate Utilities Package

This package contains all the backend utilities and helper functions for:
- Authentication and user management
- Data preprocessing and feature engineering
- Model training and prediction
- Price classification
- Property recommendations
- Session state management
- UI styling and themes
"""

__version__ = "2.0.0"
__author__ = "SmartEstate Team"
__description__ = "Industrial-Grade Real Estate Analytics Platform"

# ============================================================================
# IMPORT ALL UTILITY MODULES
# ============================================================================

# Authentication & User Management
from .auth import (
    login,
    logout,
    create_user,
    verify_user,
    load_users,
    save_users,
    hash_password,
    is_admin,
    is_authenticated,
    get_current_user,
    get_user_name,
    update_user_profile,
    delete_user_account,
    get_all_users,
    get_user_stats,
    apply_auth_theme
)

# Data Preprocessing
from .data_preprocessing import (
    load_and_preprocess_data,
    create_processed_data,
    create_sample_data,
    convert_sqft_to_numeric,
    calculate_amenity_score,
    get_feature_importance,
    BANGALORE_LOCATIONS,
    LOCATION_PRICE_FACTORS
)

# Model Training
from .model_training import (
    train_models,
    load_trained_models,
    evaluate_model,
    save_model,
    get_best_model
)

# Price Prediction
from .predict import (
    predict_price,
    get_price_category,
    predict_with_confidence,
    load_prediction_models,
    PRICE_CATEGORIES
)

# Price Classification
from .price_classifier import (
    classify_price_range,
    get_price_trend,
    compare_with_market,
    PriceClassifier
)

# Recommendation System
from .recommendation import (
    get_similar_properties,
    recommend_properties,
    get_hotspots,
    RecommendationEngine
)

# Session State Management
from .session_state import (
    init_session_state,
    save_prediction_to_history,
    get_prediction_history,
    clear_session,
    update_session  # Make sure this exists
)
# UI Styling (Theme)
from .styles import (
    apply_custom_styles,
    apply_glassmorphism,
    THEME_COLORS,
    GLASS_CARD_STYLE,
    BUTTON_STYLE
)

# ============================================================================
# PACKAGE CONFIGURATION
# ============================================================================

# Theme Configuration
THEME_CONFIG = {
    "primary_color": "#8B5CF6",      # Soft Purple
    "secondary_color": "#C4B5FD",    # Light Lavender
    "accent_color": "#F97316",       # Warm Orange
    "background_gradient": "linear-gradient(135deg, #F5F3FF, #EDE9FE)",
    "glass_bg": "rgba(255, 255, 255, 0.6)",
    "glass_blur": "blur(10px)",
    "text_dark": "#1F2937",
    "text_light": "#FFFFFF",
    "border_light": "rgba(255, 255, 255, 0.3)",
    "shadow_color": "rgba(139, 92, 246, 0.15)"
}

# Feature Flags
FEATURES = {
    "enable_advanced_options": True,
    "enable_roi_calculator": True,
    "enable_recommendations": True,
    "enable_analytics": True,
    "enable_admin_dashboard": True
}

# Model Configuration
MODEL_CONFIG = {
    "random_state": 42,
    "test_size": 0.2,
    "validation_size": 0.1,
    "n_estimators": 100,
    "max_depth": 15,
    "learning_rate": 0.1
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_package_info():
    """
    Get package information
    Returns a dictionary with package metadata
    """
    return {
        "name": "SmartEstate Utilities",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "theme": THEME_CONFIG,
        "features": FEATURES,
        "locations_count": len(BANGALORE_LOCATIONS) if 'BANGALORE_LOCATIONS' in dir() else 35
    }

def initialize_package():
    """
    Initialize the utils package
    Sets up necessary configurations and directories
    """
    import os
    
    # Create necessary directories if they don't exist
    directories = ['models', 'data', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
    
    print(f"✅ SmartEstate Utilities Package v{__version__} initialized")
    print(f"   Theme: Soft Purple + Warm Orange")
    print(f"   Features: {len(FEATURES)} enabled")
    
    return True

def get_theme_colors():
    """
    Get theme color configuration
    Returns a dictionary with all theme colors
    """
    return THEME_CONFIG.copy()

def apply_theme_to_component(component_type="card"):
    """
    Get CSS classes for different component types
    """
    themes = {
        "card": """
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
            transition: all 0.3s ease;
        """,
        "card_hover": """
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
            border-color: rgba(249, 115, 22, 0.3);
        """,
        "button": """
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        """,
        "button_hover": """
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
        """,
        "gradient_text": """
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        """
    }
    
    return themes.get(component_type, "")

# ============================================================================
# PACKAGE INITIALIZATION ON IMPORT
# ============================================================================

# Auto-initialize when package is imported
_initialized = False

def _auto_initialize():
    """Auto-initialize the package"""
    global _initialized
    if not _initialized:
        initialize_package()
        _initialized = True

# Run auto-initialization
_auto_initialize()

# ============================================================================
# EXPORTS - What gets imported with "from utils import *"
# ============================================================================

__all__ = [
    # Auth functions
    'login', 'logout', 'create_user', 'verify_user', 'load_users', 'save_users',
    'hash_password', 'is_admin', 'is_authenticated', 'get_current_user', 
    'get_user_name', 'update_user_profile', 'delete_user_account', 
    'get_all_users', 'get_user_stats', 'apply_auth_theme',
    
    # Data preprocessing
    'load_and_preprocess_data', 'create_processed_data', 'create_sample_data',
    'convert_sqft_to_numeric', 'calculate_amenity_score', 'get_feature_importance',
    'BANGALORE_LOCATIONS', 'LOCATION_PRICE_FACTORS',
    
    # Model training
    'train_models', 'load_trained_models', 'evaluate_model', 'save_model', 'get_best_model',
    
    # Prediction
    'predict_price', 'get_price_category', 'predict_with_confidence', 'load_prediction_models',
    'PRICE_CATEGORIES',
    
    # Price classification
    'classify_price_range', 'get_price_trend', 'compare_with_market', 'PriceClassifier',
    
    # Recommendations
    'get_similar_properties', 'recommend_properties', 'get_hotspots', 'RecommendationEngine',
    
    # Session state
    'initialize_session_state', 'save_prediction_to_history', 'get_prediction_history',
    'clear_session', 'update_session',
    
    # Styles
    'apply_custom_styles', 'apply_glassmorphism', 'THEME_COLORS', 'GLASS_CARD_STYLE', 'BUTTON_STYLE',
    
    # Package helpers
    'get_package_info', 'initialize_package', 'get_theme_colors', 'apply_theme_to_component',
    'THEME_CONFIG', 'FEATURES', 'MODEL_CONFIG'
]

# ============================================================================
# END OF PACKAGE INITIALIZATION
# ============================================================================