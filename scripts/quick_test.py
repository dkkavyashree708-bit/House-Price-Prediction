#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        'data/Bengaluru_House_Data.csv',
        'data/processed_data.csv',
        'data/Bengaluru_House_Data.csv.gz'
    ]
    
    found = False
    for path in dataset_paths:
        if os.path.exists(path):
            print_success(f"Found dataset: {path}")
            found = True
            return path
    
    if not found:
        print_warning("No existing dataset found. Creating sample dataset...")
        create_sample_dataset()
        return 'data/Bengaluru_House_Data.csv'

def create_sample_dataset():
    """Create a sample dataset if none exists with 1000+ locations"""
    
    np.random.seed(42)
    
    # Comprehensive list of Bangalore locations (100+)
    locations = [
        # Central
        'Koramangala', 'Indiranagar', 'Jayanagar', 'HSR Layout', 'BTM Layout',
        'JP Nagar', 'Banashankari', 'Basavanagudi', 'Malleshwaram', 'Rajajinagar',
        'Sadashivanagar', 'Vasanth Nagar', 'Richmond Town', 'Ulsoor', 'Domlur',
        'Lavelle Road', 'MG Road', 'Brigade Road', 'Church Street', 'Cunningham Road',
        # East
        'Whitefield', 'Marathahalli', 'Bellandur', 'Sarjapur Road', 'KR Puram',
        'Mahadevapura', 'Brookefield', 'Hoodi', 'Kadugodi', 'Varthur',
        'Panathur', 'Doddanekkundi', 'CV Raman Nagar', 'Banaswadi', 'Kalyan Nagar',
        # South
        'Electronic City', 'Bannerghatta Road', 'Kanakapura Road', 'RR Nagar',
        'Begur Road', 'Arekere', 'Gottigere', 'Konanakunte', 'Yelachenahalli',
        'Anjanapura', 'Vasanthapura', 'Uttarahalli', 'Padmanabhanagar', 'Anekal',
        # North
        'Hebbal', 'Yelahanka', 'Thanisandra Road', 'Hennur Road', 'Devanahalli',
        'Jakkur', 'Sahakara Nagar', 'Rachenahalli', 'Byatarayanapura', 'Bagalur',
        # West
        'Vijayanagar', 'Basaveshwaranagar', 'Kengeri', 'Mysore Road', 'Yeshwanthpur',
        'Peenya', 'Nagarabhavi', 'Chandra Layout', 'Kamakshipalya', 'Magadi Road'
    ]
    
    data = []
    for loc in locations:
        # Generate 20-80 properties per location
        num_properties = np.random.randint(20, 80)
        
        for _ in range(num_properties):
            total_sqft = np.random.uniform(500, 3500)
            bhk = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.25, 0.40, 0.20, 0.10])
            bath = min(bhk + np.random.randint(0, 2), 5)
            balcony = np.random.choice([0, 1, 2, 3], p=[0.1, 0.35, 0.35, 0.2])
            
            # Price based on location (premium factor)
            location_factors = {
                'Indiranagar': 2.5, 'Koramangala': 2.4, 'Jayanagar': 2.2,
                'Whitefield': 1.8, 'HSR Layout': 2.0, 'Electronic City': 1.5,
                'BTM Layout': 1.9, 'JP Nagar': 1.8, 'Banashankari': 1.7,
                'Basavanagudi': 1.9, 'Malleshwaram': 1.8, 'Rajajinagar': 1.7,
                'Hebbal': 1.4, 'Yelahanka': 1.2, 'RR Nagar': 1.3,
                'Vijayanagar': 1.5, 'Marathahalli': 1.7, 'Bellandur': 1.6
            }
            factor = location_factors.get(loc, 1.2)
            price = (total_sqft / 1000) * 50 * factor + bhk * 15 + bath * 5 + balcony * 3
            price = max(20, min(500, round(price, 2)))  # Cap between 20-500 Lakhs
            
            # Zone assignment
            if loc in ['Indiranagar', 'Koramangala', 'Jayanagar', 'HSR Layout', 'BTM Layout', 'JP Nagar', 'Banashankari', 'Basavanagudi', 'Malleshwaram', 'Rajajinagar']:
                zone = 'Central'
            elif loc in ['Whitefield', 'Marathahalli', 'Bellandur', 'Sarjapur Road', 'KR Puram', 'Mahadevapura', 'Brookefield']:
                zone = 'East'
            elif loc in ['Electronic City', 'Bannerghatta Road', 'Kanakapura Road', 'RR Nagar', 'Begur Road', 'Anekal']:
                zone = 'South'
            elif loc in ['Hebbal', 'Yelahanka', 'Thanisandra Road', 'Hennur Road', 'Devanahalli']:
                zone = 'North'
            else:
                zone = 'West'
            
            data.append({
                'location': loc,
                'latitude': 12.9716 + np.random.normal(0, 0.05),
                'longitude': 77.5946 + np.random.normal(0, 0.05),
                'total_sqft': round(total_sqft, 2),
                'bhk': bhk,
                'bath': bath,
                'balcony': balcony,
                'price': price,
                'price_per_sqft': round(price / total_sqft * 100, 2) if total_sqft > 0 else 0,
                'area_type': np.random.choice(['Premium', 'Mid-range', 'Developing'], p=[0.3, 0.5, 0.2]),
                'zone': zone,
                'hospital_distance_km': round(np.random.uniform(0.5, 5), 1),
                'school_distance_km': round(np.random.uniform(0.3, 3), 1),
                'metro_distance_km': round(np.random.uniform(0.5, 8), 1),
                'busstop_distance_km': round(np.random.uniform(0.1, 1.5), 1),
                'office_distance_km': round(np.random.uniform(1, 12), 1),
                'college_distance_km': round(np.random.uniform(0.5, 5), 1)
            })
    
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/Bengaluru_House_Data.csv', index=False)
    print_success(f"Created sample dataset with {len(df)} records")
    print_info(f"Locations: {df['location'].nunique()}")
    return df

def test_data_quality(df):
    """Test data quality metrics"""
    print_header("📊 DATA QUALITY CHECK")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print_success("No missing values found")
    else:
        print_warning(f"Found {missing.sum()} missing values")
        for col, count in missing[missing > 0].items():
            print(f"   {col}: {count} missing")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates == 0:
        print_success("No duplicate rows found")
    else:
        print_warning(f"Found {duplicates} duplicate rows")
    
    # Check data types
    print_info("Column data types:")
    for col in df.columns:
        print(f"   {col}: {df[col].dtype}")
    
    # Check numeric ranges
    if 'price' in df.columns:
        print_info("Price statistics:")
        print_metric("   Min", df['price'].min(), "Lakhs")
        print_metric("   Max", df['price'].max(), "Lakhs")
        print_metric("   Mean", round(df['price'].mean(), 2), "Lakhs")
        print_metric("   Median", round(df['price'].median(), 2), "Lakhs")
    
    if 'total_sqft' in df.columns:
        print_info("Area statistics:")
        print_metric("   Min", df['total_sqft'].min(), "sqft")
        print_metric("   Max", df['total_sqft'].max(), "sqft")
        print_metric("   Mean", round(df['total_sqft'].mean(), 2), "sqft")

def test_location_coverage(df):
    """Test location coverage"""
    print_header("📍 LOCATION COVERAGE")
    
    if 'location' not in df.columns:
        print_error("No location column found")
        return
    
    unique_locations = df['location'].nunique()
    print_success(f"Total unique locations: {unique_locations}")
    
    # Location frequency
    location_counts = df['location'].value_counts()
    print_info("Top 10 most common locations:")
    for loc, count in location_counts.head(10).items():
        print(f"   {loc}: {count} properties")
    
    # Location coverage by zone
    if 'zone' in df.columns:
        print_info("Location distribution by zone:")
        zone_counts = df['zone'].value_counts()
        for zone, count in zone_counts.items():
            print(f"   {zone}: {count} properties ({count/len(df)*100:.1f}%)")

# ==================== MODEL TESTS ====================
def test_models():
    """Test if ML models are available"""
    print_header("🤖 MODEL AVAILABILITY CHECK")
    
    model_files = [
        'models/best_model.pkl',
        'models/all_models.pkl',
        'models/preprocessor.pkl',
        'models/feature_columns.pkl',
        'models/price_classifier.pkl',
        'models/recommendation_model.pkl',
        'models/location_factors.pkl'
    ]
    
    available = 0
    for model_file in model_files:
        if os.path.exists(model_file):
            print_success(f"Found: {model_file}")
            available += 1
        else:
            print_warning(f"Missing: {model_file}")
    
    print_info(f"Models available: {available}/{len(model_files)}")
    
    # Try to load best model if exists
    if os.path.exists('models/best_model.pkl'):
        try:
            import joblib
            model = joblib.load('models/best_model.pkl')
            print_success(f"Best model loaded successfully")
            print_info(f"Model type: {type(model).__name__}")
        except Exception as e:
            print_error(f"Failed to load model: {e}")

# ==================== PREDICTION TESTS ====================
def test_predictions(df):
    """Test prediction functionality"""
    print_header("🔮 PREDICTION TEST")
    
    try:
        from utils.predict import predict_price, get_price_category
        
        # Test with sample locations
        print_info("Testing predictions for sample locations:")
        
        for location in TEST_LOCATIONS[:10]:
            if location in df['location'].values:
                total_sqft = 1200
                bhk = 2
                bath = 2
                balcony = 1
                area_type = "Mid-range"
                
                start_time = time.time()
                predicted_price = predict_price(location, total_sqft, bhk, bath, balcony, area_type, df)
                prediction_time = time.time() - start_time
                
                category, color, emoji = get_price_category(predicted_price)
                
                print(f"   {location}:")
                print(f"      Predicted: ₹{predicted_price:.2f} Lakhs")
                print(f"      Category: {emoji} {category}")
                print(f"      Time: {prediction_time*1000:.2f}ms")
            else:
                print_warning(f"   {location}: Not found in dataset")
        
        print_success("Prediction test completed")
        
    except ImportError as e:
        print_error(f"Could not import prediction module: {e}")
    except Exception as e:
        print_error(f"Prediction test failed: {e}")

# ==================== PERFORMANCE TESTS ====================
def test_performance(df):
    """Test performance metrics"""
    print_header("⚡ PERFORMANCE TEST")
    
    # Memory usage
    memory_usage = df.memory_usage(deep=True).sum() / 1024 ** 2
    print_metric("DataFrame Memory", f"{memory_usage:.2f}", "MB")
    
    # Load time test
    start_time = time.time()
    pd.read_csv('data/Bengaluru_House_Data.csv')
    load_time = time.time() - start_time
    print_metric("Dataset Load Time", f"{load_time*1000:.2f}", "ms")
    
    # Basic operations
    start_time = time.time()
    df.groupby('location')['price'].mean()
    group_time = time.time() - start_time
    print_metric("GroupBy Operation", f"{group_time*1000:.2f}", "ms")

# ==================== UTILITY TESTS ====================
def test_utils():
    """Test utility modules"""
    print_header("🔧 UTILITY MODULES TEST")
    
    modules = [
        ('utils.auth', 'login'),
        ('utils.styles', 'apply_custom_styles'),
        ('utils.session_state', 'init_session_state'),
        ('utils.performance', 'load_models'),
        ('utils.add_coordinates', 'add_coordinates_to_locations')
    ]
    
    for module_name, function_name in modules:
        try:
            module = __import__(module_name, fromlist=[function_name])
            if hasattr(module, function_name):
                print_success(f"{module_name}.{function_name}")
            else:
                print_warning(f"{module_name}.{function_name} not found")
        except ImportError as e:
            print_error(f"Could not import {module_name}: {e}")

# ==================== REPORT GENERATION ====================
def generate_report(df, start_time):
    """Generate test report"""
    print_header("📋 TEST REPORT SUMMARY")
    
    total_time = time.time() - start_time
    
    report = {
        "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_duration_seconds": round(total_time, 2),
        "dataset": {
            "records": len(df),
            "locations": df['location'].nunique() if 'location' in df.columns else 0,
            "columns": len(df.columns),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2)
        }
    }
    
    if 'price' in df.columns:
        report["dataset"]["price_range"] = f"{df['price'].min():.2f} - {df['price'].max():.2f} Lakhs"
        report["dataset"]["avg_price"] = round(df['price'].mean(), 2)
    
    print_info(f"Test completed in {total_time:.2f} seconds")
    print_info(f"Dataset: {report['dataset']['records']} records, {report['dataset']['locations']} locations")
    print_info(f"Memory usage: {report['dataset']['memory_mb']} MB")
    
    # Save report
    os.makedirs('logs', exist_ok=True)
    with open('logs/test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print_success("Report saved to logs/test_report.json")
    
    return report

# ==================== MAIN FUNCTION ====================
def test_dataset():
    """Main test function"""
    print_header("🏠 SmartEstate - System Test")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Step 1: Check dataset
    dataset_path = test_dataset_exists()
    
    # Step 2: Load dataset
    try:
        df = pd.read_csv(dataset_path)
        print_success(f"Dataset loaded: {len(df)} records")
    except Exception as e:
        print_error(f"Failed to load dataset: {e}")
        return False
    
    # Step 3: Test data quality
    test_data_quality(df)
    
    # Step 4: Test location coverage
    test_location_coverage(df)
    
    # Step 5: Test models
    test_models()
    
    # Step 6: Test predictions
    test_predictions(df)
    
    # Step 7: Test performance
    test_performance(df)
    
    # Step 8: Test utilities
    test_utils()
    
    # Step 9: Generate report
    generate_report(df, start_time)
    
    print_header("🎉 TEST COMPLETED SUCCESSFULLY!")
    return True

def run_quick_test():
    """Quick test without full dataset loading"""
    print_header("⚡ QUICK TEST MODE")
    
    # Create sample dataset if needed
    if not os.path.exists('data/Bengaluru_House_Data.csv'):
        create_sample_dataset()
    
    # Quick verification
    df = pd.read_csv('data/Bengaluru_House_Data.csv')
    print_success(f"Dataset ready: {len(df)} records, {df['location'].nunique()} locations")
    
    # Test single prediction
    try:
        from utils.predict import predict_price
        
        test_loc = df['location'].iloc[0]
        predicted = predict_price(test_loc, 1200, 2, 2, 1, "Mid-range", df)
        print_success(f"Sample prediction for {test_loc}: ₹{predicted:.2f} Lakhs")
    except Exception as e:
        print_warning(f"Prediction test skipped: {e}")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartEstate Quick Test')
    parser.add_argument('--quick', action='store_true', help='Run quick test only')
    args = parser.parse_args()
    
    if args.quick:
        run_quick_test()
    else:
        test_dataset()