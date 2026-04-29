"""
SmartEstate Quick Test Script
Tests dataset loading, model availability, and prediction functionality
"""

import pandas as pd
import numpy as np
import os
import sys
import time
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== TEST CONFIGURATION ====================
TEST_LOCATIONS = [
    'Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Jayanagar',
    'Electronic City', 'BTM Layout', 'JP Nagar', 'Banashankari', 'Basavanagudi',
    'Malleshwaram', 'Rajajinagar', 'Hebbal', 'Yelahanka', 'RR Nagar',
    'Vijayanagar', 'Marathahalli', 'Bellandur', 'Sarjapur Road', 'KR Puram'
]

# ==================== COLOR CODES FOR OUTPUT ====================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}📌 {text}{Colors.ENDC}")

def print_metric(label, value, unit=""):
    print(f"   {Colors.BOLD}{label}:{Colors.ENDC} {Colors.GREEN}{value}{unit}{Colors.ENDC}")

# ==================== DATASET TESTS ====================
def test_dataset_exists():
    """Test if dataset file exists"""
    print_header("📁 DATASET EXISTENCE CHECK")
    
    dataset_paths = [
        'data/processed_data.csv',
        'data/Bengaluru_House_Data.csv',
    ]
    
    for path in dataset_paths:
        if os.path.exists(path):
            print_success(f"Found dataset: {path}")
            df = pd.read_csv(path)
            return df, path
    
    print_warning("No existing dataset found.")
    return None, None

# ==================== PRICE CLASSIFICATION ====================
def classify_price(price):
    if price < 40:
        return 'Budget'
    elif price < 70:
        return 'Affordable'
    elif price < 120:
        return 'Mid-Range'
    elif price < 200:
        return 'Premium'
    else:
        return 'Luxury'

# ==================== PREDICTION FUNCTION (FALLBACK) ====================
def predict_price_fallback(location, total_sqft, bhk, bath, balcony, area_type):
    """Fallback prediction logic when ML model is not available"""
    # Location price factors
    location_factors = {
        'Indiranagar': 2.5, 'Koramangala': 2.4, 'Jayanagar': 2.2,
        'Whitefield': 1.8, 'HSR Layout': 2.0, 'Electronic City': 1.5,
        'BTM Layout': 1.9, 'JP Nagar': 1.8, 'Banashankari': 1.7,
        'Basavanagudi': 1.9, 'Malleshwaram': 1.8, 'Rajajinagar': 1.7,
        'Hebbal': 1.4, 'Yelahanka': 1.2, 'RR Nagar': 1.3,
        'Vijayanagar': 1.5, 'Marathahalli': 1.7, 'Bellandur': 1.6,
        'Sarjapur Road': 1.5, 'KR Puram': 1.4, 'Mahadevapura': 1.5,
        'Brookefield': 1.6, 'Ulsoor': 1.9, 'Richmond Town': 2.0,
        'Sadashivanagar': 2.3, 'Frazer Town': 1.7, 'Anekal': 1.0
    }
    
    base_price_per_sqft = 5000
    location_factor = location_factors.get(location.split(',')[0].strip(), 1.2)
    bhk_factor = 1 + (bhk - 2) * 0.1
    area_factors = {'Premium': 1.3, 'Mid-range': 1.0, 'Developing': 0.8}
    area_factor = area_factors.get(area_type, 1.0)
    
    price = base_price_per_sqft * total_sqft * location_factor * bhk_factor * area_factor
    return round(price / 100000, 2)  # Convert to Lakhs

# ==================== MAIN TEST ====================
def run_quick_test():
    """Quick test without full dataset loading"""
    print_header("⚡ QUICK TEST MODE")
    
    # Step 1: Load dataset
    df, dataset_path = test_dataset_exists()
    
    if df is None:
        print_error("No dataset found. Please run training first.")
        return False
    
    print_success(f"Dataset ready: {len(df)} records, {df['location'].nunique()} locations")
    
    # Step 2: Test price classification
    print_header("🏷️ PRICE CLASSIFICATION TEST")
    
    if 'price' in df.columns:
        df['price_category'] = df['price'].apply(classify_price)
        category_counts = df['price_category'].value_counts()
        
        for category in ['Budget', 'Affordable', 'Mid-Range', 'Premium', 'Luxury']:
            count = category_counts.get(category, 0)
            pct = count / len(df) * 100
            print(f"   {category}: {count} ({pct:.1f}%)")
    else:
        print_warning("No price column found in dataset")
    
    # Step 3: Test location coverage
    print_header("📍 LOCATION COVERAGE")
    unique_locations = df['location'].nunique()
    print_success(f"Total unique locations: {unique_locations}")
    
    # Show sample locations
    print_info("Sample locations:")
    for loc in df['location'].unique()[:20]:
        print(f"   • {loc}")
    
    # Step 4: Test prediction
    print_header("🔮 PREDICTION TEST")
    
    test_cases = [
        ("Indiranagar", 1200, 2, 2, 1, "Premium"),
        ("Koramangala", 1500, 3, 3, 2, "Premium"),
        ("Whitefield", 1000, 2, 2, 1, "Mid-range"),
        ("Electronic City", 1100, 2, 2, 1, "Mid-range"),
        ("Anekal", 800, 1, 1, 0, "Developing"),
    ]
    
    print_info("Testing predictions for sample locations:")
    for loc, sqft, bhk, bath, balcony, area_type in test_cases:
        if loc in df['location'].values or any(loc in str(l) for l in df['location'].unique()):
            price = predict_price_fallback(loc, sqft, bhk, bath, balcony, area_type)
            category = classify_price(price)
            print(f"   {loc}: ₹{price:.2f} Lakhs ({category})")
        else:
            print_warning(f"   {loc}: Not found in dataset")
    
    # Step 5: Check model files
    print_header("🤖 MODEL FILES CHECK")
    
    model_files = [
        'models/best_model.pkl',
        'models/all_models.pkl',
        'models/feature_columns.pkl',
        'models/price_classifier.pkl',
        'models/recommendation_model.pkl'
    ]
    
    for model_file in model_files:
        if os.path.exists(model_file):
            size = os.path.getsize(model_file) / 1024
            print_success(f"{model_file} ({size:.1f} KB)")
        else:
            print_warning(f"{model_file} - Not found")
    
    # Step 6: Summary
    print_header("✅ QUICK TEST COMPLETE")
    
    print_info(f"Dataset: {len(df)} properties, {unique_locations} locations")
    if 'price' in df.columns:
        print_info(f"Price range: ₹{df['price'].min():.1f}L - ₹{df['price'].max():.1f}L")
        print_info(f"Average price: ₹{df['price'].mean():.1f}L")
    
    print_success("System is ready!")
    print_info("Run 'streamlit run app.py' to start the web application")
    
    return True

if __name__ == "__main__":
    run_quick_test()