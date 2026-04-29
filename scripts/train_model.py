"""
SmartEstate - Simplified Training Pipeline (FIXED)
Faster training with essential models only
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== COLOR CODES ====================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}📌 {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")

# Create models directory
os.makedirs('models', exist_ok=True)

print_header("🏠 SMARTESTATE - TRAINING PIPELINE")

# Step 1: Load processed data
print_info("Loading processed data...")

# Try multiple possible file paths
possible_paths = [
    'data/processed_data.csv',
    'data/Bengaluru_House_Data.csv',
    '../data/processed_data.csv',
    '../data/Bengaluru_House_Data.csv'
]

df = None
for path in possible_paths:
    if os.path.exists(path):
        df = pd.read_csv(path)
        print_success(f"Loaded {len(df)} records from {path}")
        break

if df is None:
    print_warning("No dataset found. Creating sample data...")
    # Create sample data
    np.random.seed(42)
    locations = ['Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Jayanagar',
                 'Electronic City', 'BTM Layout', 'JP Nagar', 'Banashankari', 'Malleshwaram']
    data = []
    for loc in locations:
        for _ in range(100):
            total_sqft = np.random.uniform(500, 3000)
            bhk = np.random.choice([1, 2, 3, 4])
            bath = min(bhk + np.random.randint(0, 2), 5)
            balcony = np.random.choice([0, 1, 2])
            price = (total_sqft / 1000) * 50 + bhk * 15 + bath * 5 + balcony * 3
            price = max(20, min(500, round(price, 2)))
            data.append({
                'location': loc,
                'total_sqft': total_sqft,
                'bhk': bhk,
                'bath': bath,
                'balcony': balcony,
                'price': price,
                'price_per_sqft': price / total_sqft * 100
            })
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/processed_data.csv', index=False)
    print_success(f"Created sample data with {len(df)} records")

# Step 2: Add price classification
print_header("🏷️ ADDING PRICE CLASSIFICATION")

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

if 'price' in df.columns:
    df['price_category'] = df['price'].apply(classify_price)
    
    category_counts = df['price_category'].value_counts()
    for cat in ['Budget', 'Affordable', 'Mid-Range', 'Premium', 'Luxury']:
        count = category_counts.get(cat, 0)
        pct = count / len(df) * 100
        print(f"   {cat}: {count} ({pct:.1f}%)")
else:
    print_warning("No price column found")

# Step 3: Prepare features
print_header("🔧 PREPARING FEATURES")

# Define feature columns
exclude_cols = ['price', 'location', 'availability', 'size', 'society', 'area_type',
                'latitude', 'longitude', 'price_category', 'Unnamed: 0', 'index', 'id']

# Get numeric feature columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
feature_cols = [col for col in numeric_cols if col not in exclude_cols]

# Add derived features if they exist
derived_features = ['price_per_sqft', 'total_rooms', 'sqft_per_bhk']
for feat in derived_features:
    if feat in df.columns and feat not in feature_cols:
        feature_cols.append(feat)

print_success(f"Using {len(feature_cols)} features for modeling")
print_info(f"Features: {', '.join(feature_cols[:10])}" + 
           (f" and {len(feature_cols)-10} more..." if len(feature_cols) > 10 else ""))

# Step 4: Train models (simplified)
print_header("🤖 TRAINING MODELS")

try:
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    import joblib
    
    # Split data
    X = df[feature_cols].fillna(0)
    y = df['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print_info(f"Training data: {len(X_train)} samples")
    print_info(f"Testing data: {len(X_test)} samples")
    
    results = {}
    models = {}
    
    # Linear Regression
    print("\n   Training Linear Regression...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    results['Linear Regression'] = {
        'r2': r2_score(y_test, y_pred),
        'mae': mean_absolute_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
    }
    models['Linear Regression'] = lr
    print(f"      R²: {results['Linear Regression']['r2']:.4f}, MAE: {results['Linear Regression']['mae']:.2f}")
    
    # Ridge Regression
    print("\n   Training Ridge Regression...")
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train, y_train)
    y_pred = ridge.predict(X_test)
    results['Ridge Regression'] = {
        'r2': r2_score(y_test, y_pred),
        'mae': mean_absolute_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
    }
    models['Ridge Regression'] = ridge
    print(f"      R²: {results['Ridge Regression']['r2']:.4f}, MAE: {results['Ridge Regression']['mae']:.2f}")
    
    # Random Forest
    print("\n   Training Random Forest (may take a moment)...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    results['Random Forest'] = {
        'r2': r2_score(y_test, y_pred),
        'mae': mean_absolute_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
    }
    models['Random Forest'] = rf
    print(f"      R²: {results['Random Forest']['r2']:.4f}, MAE: {results['Random Forest']['mae']:.2f}")
    
    # Find best model
    best_model_name = max(results, key=lambda x: results[x]['r2'])
    best_model = models[best_model_name]
    
    print_header("🏆 MODEL COMPARISON RESULTS")
    results_df = pd.DataFrame(results).T.sort_values('r2', ascending=False)
    print(results_df.round(4).to_string())
    
    print(f"\n{Colors.GREEN}🏆 BEST MODEL: {best_model_name}{Colors.ENDC}")
    print(f"   R² Score: {results[best_model_name]['r2']:.4f}")
    print(f"   MAE: {results[best_model_name]['mae']:.2f} Lakhs")
    
    # Save models
    print_header("💾 SAVING MODELS")
    
    joblib.dump(best_model, 'models/best_model.pkl')
    print_success("best_model.pkl saved")
    
    joblib.dump(models, 'models/all_models.pkl')
    print_success("all_models.pkl saved")
    
    joblib.dump(feature_cols, 'models/feature_columns.pkl')
    print_success("feature_columns.pkl saved")
    
    results_df.to_csv('models/model_results.csv')
    print_success("model_results.csv saved")
    
    # Save preprocessor info
    preprocessor_info = {
        'feature_cols': feature_cols,
        'n_features': len(feature_cols),
        'n_samples': len(df)
    }
    joblib.dump(preprocessor_info, 'models/preprocessor.pkl')
    print_success("preprocessor.pkl saved")
    
    # Save price classifier
    price_classifier = {
        'classify': classify_price,
        'budget_threshold': 40,
        'affordable_threshold': 70,
        'mid_threshold': 120,
        'premium_threshold': 200
    }
    joblib.dump(price_classifier, 'models/price_classifier.pkl')
    print_success("price_classifier.pkl saved")
    
    # Step 5: Build recommendation system
    print_header("🎯 BUILDING RECOMMENDATION SYSTEM")
    
    try:
        from sklearn.neighbors import NearestNeighbors
        from sklearn.preprocessing import MinMaxScaler
        
        rec_features = ['total_sqft', 'bhk', 'bath', 'balcony', 'price']
        rec_features = [f for f in rec_features if f in df.columns]
        
        print_info(f"Using features for recommendation: {rec_features}")
        
        rec_data = df[rec_features].fillna(df[rec_features].median())
        scaler = MinMaxScaler()
        rec_data_scaled = scaler.fit_transform(rec_data)
        
        knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
        knn.fit(rec_data_scaled)
        
        recommendation_model = {
            'knn': knn,
            'scaler': scaler,
            'features': rec_features,
            'sample_data': df[rec_features].head(1000).to_dict()
        }
        joblib.dump(recommendation_model, 'models/recommendation_model.pkl')
        print_success("recommendation_model.pkl saved")
    except Exception as e:
        print_warning(f"Recommendation system error: {e}")
    
    print_header("✅ TRAINING COMPLETE!")
    print_info(f"Dataset: {len(df)} properties, {len(feature_cols)} features")
    print_info(f"Best Model: {best_model_name}")
    print_info(f"R² Score: {results[best_model_name]['r2']:.4f}")
    print_info("You can now run: streamlit run app.py")
    
except Exception as e:
    print_error(f"Training failed: {e}")
    import traceback
    traceback.print_exc()