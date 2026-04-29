import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import re
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
RANDOM_STATE = 42
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# 30+ Bangalore locations for mapping
BANGALORE_LOCATIONS = [
    'Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Jayanagar',
    'Electronic City', 'Hebbal', 'Yelahanka', 'BTM Layout', 'JP Nagar',
    'Banashankari', 'Malleshwaram', 'Rajajinagar', 'Vijayanagar', 'Basaveshwaranagar',
    'Marathahalli', 'Bellandur', 'Sarjapur Road', 'KR Puram', 'Mahadevapura',
    'Brookefield', 'Ulsoor', 'Richmond Town', 'Sadashivanagar', 'Frazer Town',
    'RR Nagar', 'Kengeri', 'Yeshwanthpur', 'Peenya', 'Nagarabhavi',
    'Anekal', 'Devanahalli', 'Jakkur', 'Thanisandra Road', 'Hennur Road'
]

# Location price factors (based on actual market data)
LOCATION_PRICE_FACTORS = {
    'Indiranagar': 2.5, 'Koramangala': 2.4, 'Whitefield': 1.8, 'HSR Layout': 2.0,
    'Jayanagar': 2.2, 'Electronic City': 1.5, 'Hebbal': 1.4, 'Yelahanka': 1.2,
    'BTM Layout': 1.9, 'JP Nagar': 1.8, 'Banashankari': 1.7, 'Malleshwaram': 1.8,
    'Rajajinagar': 1.7, 'Vijayanagar': 1.5, 'Basaveshwaranagar': 1.4, 'Marathahalli': 1.7,
    'Bellandur': 1.6, 'Sarjapur Road': 1.5, 'KR Puram': 1.4, 'Mahadevapura': 1.5,
    'Brookefield': 1.6, 'Ulsoor': 1.9, 'Richmond Town': 2.0, 'Sadashivanagar': 2.3,
    'Frazer Town': 1.7, 'RR Nagar': 1.3, 'Kengeri': 1.2, 'Yeshwanthpur': 1.3,
    'Peenya': 1.1, 'Nagarabhavi': 1.3, 'Anekal': 1.0, 'Devanahalli': 1.0,
    'Jakkur': 1.2, 'Thanisandra Road': 1.3, 'Hennur Road': 1.3
}

def convert_sqft_to_numeric(value):
    """
    Convert sqft value to numeric
    Handles ranges like "1200 - 1500" and returns average
    """
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        value = value.strip().lower()
        
        # Handle ranges like "1200 - 1500"
        if '-' in value:
            parts = value.split('-')
            try:
                start = float(parts[0].strip())
                end = float(parts[1].strip())
                return (start + end) / 2
            except:
                return None
        
        # Handle values like "1200 sqft"
        match = re.search(r'(\d+(?:\.\d+)?)', value)
        if match:
            return float(match.group(1))
    
    return None

def extract_bhk_from_area(area_type):
    """
    Extract BHK from area type description
    """
    if pd.isna(area_type):
        return None
    
    area_type = str(area_type).lower()
    match = re.search(r'(\d+)\s*bhk', area_type)
    if match:
        return int(match.group(1))
    
    return None

def calculate_amenity_score(row, amenity_cols):
    """
    Calculate amenity score based on proximity to amenities
    Lower distance = higher score
    """
    score = 0
    count = 0
    
    for col in amenity_cols:
        if col in row and pd.notna(row[col]):
            # Inverse relationship: closer amenities = higher score
            distance = min(row[col], 5)  # Cap at 5km
            score += (5 - distance) / 5
            count += 1
    
    if count > 0:
        return score / count * 5  # Scale to 0-5
    return 3.5  # Default moderate score

def load_and_preprocess_data(filepath='data/Bengaluru_House_Data.csv'):
    """
    Load and preprocess the Bangalore housing dataset
    """
    print("=" * 60)
    print("📊 DATA PREPROCESSING PIPELINE")
    print("=" * 60)
    
    # Load data
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(df)} records from {filepath}")
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        print("Creating sample data for testing...")
        df = create_sample_data()
    
    # Display initial info
    print(f"\n📋 Initial columns: {list(df.columns)}")
    
    # ==================== 1. CONVERT TOTAL_SQFT ====================
    if 'total_sqft' in df.columns:
        df['total_sqft'] = df['total_sqft'].apply(convert_sqft_to_numeric)
        print(f"✅ Converted total_sqft: {df['total_sqft'].notna().sum()} valid values")
    
    # ==================== 2. CONVERT PRICE ====================
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        print(f"✅ Converted price: {df['price'].notna().sum()} valid values")
    
    # ==================== 3. HANDLE BHK ====================
    if 'bhk' in df.columns:
        df['bhk'] = pd.to_numeric(df['bhk'], errors='coerce')
    elif 'area_type' in df.columns:
        df['bhk'] = df['area_type'].apply(extract_bhk_from_area)
        print(f"✅ Extracted bhk from area_type")
    
    # ==================== 4. CONVERT OTHER NUMERIC COLUMNS ====================
    numeric_cols = ['bath', 'balcony', 'bedroom', 'hall']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ==================== 5. HANDLE MISSING VALUES ====================
    initial_rows = len(df)
    df = df.dropna(subset=['total_sqft', 'price', 'bhk'])
    print(f"✅ Dropped {initial_rows - len(df)} rows with missing critical values")
    
    # ==================== 6. REMOVE OUTLIERS ====================
    # Remove unrealistic BHK values
    df = df[(df['bhk'] >= 1) & (df['bhk'] <= 10)]
    
    # Remove unrealistic sqft per BHK (less than 300 sqft or more than 3000 sqft per BHK)
    df['sqft_per_bhk'] = df['total_sqft'] / df['bhk']
    df = df[(df['sqft_per_bhk'] >= 300) & (df['sqft_per_bhk'] <= 3000)]
    df = df.drop(columns=['sqft_per_bhk'])
    
    # Remove price outliers (beyond 3 standard deviations)
    if len(df) > 0:
        price_mean = df['price'].mean()
        price_std = df['price'].std()
        df = df[(df['price'] >= price_mean - 3*price_std) & (df['price'] <= price_mean + 3*price_std)]
    
    print(f"✅ After outlier removal: {len(df)} records")
    
    # ==================== 7. CREATE DERIVED FEATURES ====================
    # Price per sqft
    df['price_per_sqft'] = df['price'] / df['total_sqft']
    
    # Total rooms
    if 'bath' in df.columns:
        df['total_rooms'] = df['bhk'] + df['bath']
    else:
        df['total_rooms'] = df['bhk'] * 1.5
    
    # Location score based on price factors
    df['location_score'] = df['location'].map(LOCATION_PRICE_FACTORS).fillna(1.0)
    
    # ==================== 8. AMENITY SCORE ====================
    amenity_cols = ['hospital_distance_km', 'school_distance_km', 'metro_distance_km', 
                    'busstop_distance_km', 'office_distance_km', 'college_distance_km']
    available_amenities = [col for col in amenity_cols if col in df.columns]
    
    if available_amenities:
        df['amenity_score'] = df.apply(lambda row: calculate_amenity_score(row, available_amenities), axis=1)
        print(f"✅ Calculated amenity score using {len(available_amenities)} amenities")
    else:
        df['amenity_score'] = 3.5
        print("⚠️ No amenity columns found, using default score")
    
    # ==================== 9. ENCODE CATEGORICAL VARIABLES ====================
    label_encoders = {}
    categorical_cols = ['location', 'area_type'] if 'area_type' in df.columns else ['location']
    
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le
            print(f"✅ Encoded {col}: {len(le.classes_)} unique values")
    
    # ==================== 10. SELECT FEATURES FOR MODELING ====================
    feature_cols = ['total_sqft', 'bhk', 'amenity_score', 'location_score']
    
    # Add bathroom if available
    if 'bath' in df.columns:
        feature_cols.append('bath')
    
    # Add balcony if available
    if 'balcony' in df.columns:
        feature_cols.append('balcony')
    
    # Add encoded columns
    for col in categorical_cols:
        if col + '_encoded' in df.columns:
            feature_cols.append(col + '_encoded')
    
    # Add available amenity columns
    for col in available_amenities[:3]:
        if col in df.columns:
            feature_cols.append(col)
    
    # ==================== 11. PREPARE X AND Y ====================
    X = df[feature_cols].fillna(df[feature_cols].median())
    y = df['price']
    
    print(f"\n📊 Feature set: {len(feature_cols)} features")
    print(f"   Features: {feature_cols}")
    
    # ==================== 12. SPLIT DATA ====================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    
    # Further split training for validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=VALIDATION_SIZE, random_state=RANDOM_STATE
    )
    
    print(f"\n📊 Data Split:")
    print(f"   Training: {X_train.shape[0]} samples")
    print(f"   Validation: {X_val.shape[0]} samples")
    print(f"   Test: {X_test.shape[0]} samples")
    
    # ==================== 13. SCALE FEATURES ====================
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # ==================== 14. SAVE PREPROCESSOR ====================
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/preprocessor.pkl')
    joblib.dump(feature_cols, 'models/feature_columns.pkl')
    joblib.dump(label_encoders, 'models/label_encoders.pkl')
    joblib.dump(LOCATION_PRICE_FACTORS, 'models/location_factors.pkl')
    
    print("\n✅ Preprocessing complete!")
    print("=" * 60)
    
    return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, df, feature_cols

def create_sample_data():
    """
    Create sample data for testing when real data is not available
    """
    np.random.seed(42)
    
    n_samples = 2000
    
    # Generate data
    locations = np.random.choice(BANGALORE_LOCATIONS, n_samples)
    bhk = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.35, 0.35, 0.15, 0.05])
    total_sqft = bhk * np.random.normal(550, 100, n_samples) + np.random.normal(200, 80, n_samples)
    bath = np.clip(bhk + np.random.choice([-1, 0, 1], n_samples, p=[0.1, 0.7, 0.2]), 1, 6)
    balcony = np.random.choice([0, 1, 2, 3], n_samples, p=[0.2, 0.4, 0.3, 0.1])
    
    # Price based on location factor
    location_factor = [LOCATION_PRICE_FACTORS.get(loc, 1.0) for loc in locations]
    base_price = total_sqft * 5000 * np.array(location_factor)
    price = base_price * np.random.normal(1, 0.15, n_samples)
    
    data = {
        'location': locations,
        'total_sqft': total_sqft,
        'bhk': bhk,
        'bath': bath,
        'balcony': balcony,
        'price': price,
        'area_type': np.random.choice(['Premium', 'Mid-range', 'Developing'], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Add amenity columns
    df['school_distance_km'] = np.random.uniform(0.5, 5, n_samples)
    df['hospital_distance_km'] = np.random.uniform(0.5, 5, n_samples)
    df['metro_distance_km'] = np.random.uniform(0.5, 5, n_samples)
    
    # Save sample data
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/Bengaluru_House_Data.csv', index=False)
    print(f"✅ Created sample data with {n_samples} records")
    
    return df

def create_processed_data():
    """
    Create processed data file for quick loading
    """
    print("\n" + "=" * 60)
    print("📁 CREATING PROCESSED DATA FILE")
    print("=" * 60)
    
    try:
        # Load raw data
        df = pd.read_csv('data/Bengaluru_House_Data.csv')
        print(f"✅ Loaded {len(df)} records")
        
        # Convert total_sqft to numeric
        if 'total_sqft' in df.columns:
            df['total_sqft'] = df['total_sqft'].apply(convert_sqft_to_numeric)
        
        # Convert numeric columns
        numeric_cols = ['price', 'bhk', 'bath', 'balcony']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows with missing values
        df = df.dropna()
        print(f"✅ After cleaning: {len(df)} records")
        
        # Add derived features
        df['price_per_sqft'] = df['price'] / df['total_sqft']
        df['total_rooms'] = df['bhk'] + df['bath'] if 'bath' in df.columns else df['bhk'] * 1.5
        
        # Location score
        df['location_score'] = df['location'].map(LOCATION_PRICE_FACTORS).fillna(1.0)
        
        # Amenity score
        amenity_cols = ['hospital_distance_km', 'school_distance_km', 'metro_distance_km', 
                        'busstop_distance_km', 'office_distance_km']
        available_amenities = [col for col in amenity_cols if col in df.columns]
        
        if available_amenities:
            df['amenity_score'] = df.apply(lambda row: calculate_amenity_score(row, available_amenities), axis=1)
        else:
            df['amenity_score'] = 3.5
        
        # Save processed data
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/processed_data.csv', index=False)
        
        print(f"\n✅ Processed data saved to data/processed_data.csv")
        print(f"   Total records: {len(df)}")
        print(f"   Features: {len(df.columns)}")
        print(f"   Location coverage: {df['location'].nunique()} unique locations")
        
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Creating sample data instead...")
        return create_sample_data()

def get_feature_importance(model, feature_cols):
    """
    Extract feature importance from trained model
    """
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importance = np.abs(model.coef_[0]) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
    else:
        return None
    
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    return feature_importance

if __name__ == "__main__":
    # Run preprocessing
    create_processed_data()
    
    # Load and preprocess for modeling
    X_train, X_val, X_test, y_train, y_val, y_test, df, features = load_and_preprocess_data()
    
    print("\n✅ Data preprocessing completed successfully!")