"""
SmartEstate - Simplified Training Pipeline (FIXED)
Faster training with essential models only
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import warnings
import os
import sys

warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import XGBoost
try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("⚠️ XGBoost not available, skipping...")

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

def print_metric(label, value):
    print(f"   {Colors.BOLD}{label}:{Colors.ENDC} {Colors.GREEN}{value}{Colors.ENDC}")

# Create models directory
os.makedirs('models', exist_ok=True)

print_header("🏠 SMARTESTATE - SIMPLIFIED TRAINING PIPELINE")

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
    locations = ['Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Jayanagar']
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

print_info(f"Dataset shape: {df.shape}")
print_info(f"Columns: {list(df.columns)}")

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

def get_price_emoji(price):
    if price < 40:
        return '🟢'
    elif price < 70:
        return '🟡'
    elif price < 120:
        return '🟠'
    elif price < 200:
        return '🔴'
    else:
        return '💎'

if 'price' in df.columns:
    df['price_category'] = df['price'].apply(classify_price)
    
    # Print distribution
    category_counts = df['price_category'].value_counts()
    for cat in ['Budget', 'Affordable', 'Mid-Range', 'Premium', 'Luxury']:
        count = category_counts.get(cat, 0)
        pct = count / len(df) * 100
        emoji = get_price_emoji(0)
        bar = '█' * int(pct / 2)
        print(f"   {emoji} {cat:<12}: {count:4} ({pct:5.1f}%) {bar}")
else:
    print_warning("No price column found")

# Step 3: Prepare features
print_header("🔧 PREPARING FEATURES")

# Define feature columns (exclude non-feature columns)
exclude_cols = ['price', 'availability', 'size', 'society', 'area_type', 
                'location_encoded', 'latitude', 'longitude', 'price_category',
                'Unnamed: 0', 'index', 'id', 'location']

# Also exclude any string/object columns
string_cols = df.select_dtypes(include=['object']).columns.tolist()
exclude_cols.extend(string_cols)

# Get numeric feature columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
feature_cols = [col for col in numeric_cols if col not in exclude_cols]

# Add derived features if they exist
derived_features = ['price_per_sqft', 'total_rooms', 'sqft_per_bhk', 'amenity_score']
for feat in derived_features:
    if feat in df.columns and feat not in feature_cols:
        feature_cols.append(feat)

print_success(f"Using {len(feature_cols)} features for modeling")
print_info(f"Features: {', '.join(feature_cols[:10])}" + 
           (f" and {len(feature_cols)-10} more..." if len(feature_cols) > 10 else ""))

# Step 4: Split data
print_header("📊 SPLITTING DATA")

X = df[feature_cols].fillna(0)
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print_success(f"Training: {len(X_train)} samples")
print_success(f"Testing: {len(X_test)} samples")

# Step 5: Train models
print_header("🤖 TRAINING MODELS")

results = {}

# Helper function to train and evaluate
def train_and_evaluate(name, model):
    print(f"\n   Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"      R²: {r2:.4f} | MAE: {mae:.2f}L | RMSE: {rmse:.2f}L")
    return {'model': model, 'r2': r2, 'mae': mae, 'rmse': rmse}

# 1. Linear Regression
lr = LinearRegression()
results['Linear Regression'] = train_and_evaluate('Linear Regression', lr)

# 2. Ridge Regression
ridge = Ridge(alpha=1.0)
results['Ridge Regression'] = train_and_evaluate('Ridge Regression', ridge)

# 3. Lasso Regression
lasso = Lasso(alpha=0.01)
results['Lasso Regression'] = train_and_evaluate('Lasso Regression', lasso)

# 4. Decision Tree
dt = DecisionTreeRegressor(max_depth=10, random_state=42)
results['Decision Tree'] = train_and_evaluate('Decision Tree', dt)

# 5. Random Forest
print(f"\n   Training Random Forest (may take a moment)...")
rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
results['Random Forest'] = train_and_evaluate('Random Forest', rf)

# 6. Gradient Boosting
gb = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
results['Gradient Boosting'] = train_and_evaluate('Gradient Boosting', gb)

# 7. XGBoost (if available)
if XGB_AVAILABLE:
    xgb = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, verbosity=0)
    results['XGBoost'] = train_and_evaluate('XGBoost', xgb)

# Step 6: Compare models
print_header("🏆 MODEL COMPARISON RESULTS")

results_df = pd.DataFrame({
    name: {
        'R² Score': res['r2'],
        'MAE (Lakhs)': res['mae'],
        'RMSE (Lakhs)': res['rmse']
    } for name, res in results.items()
}).T.sort_values('R² Score', ascending=False)

print("\n" + results_df.round(4).to_string())

# Select best model
best_model_name = results_df.index[0]
best_model = results[best_model_name]['model']

print(f"\n{Colors.GREEN}🏆 BEST MODEL: {best_model_name}{Colors.ENDC}")
print_metric("   R² Score", f"{results_df.loc[best_model_name, 'R² Score']:.4f}")
print_metric("   MAE", f"{results_df.loc[best_model_name, 'MAE (Lakhs)']:.2f} Lakhs")

# Step 7: Feature Importance
print_header("📊 FEATURE IMPORTANCE")

if hasattr(best_model, 'feature_importances_'):
    importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': best_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\n   Top 10 Most Important Features:")
    for i in range(min(10, len(importance_df))):
        print(f"   {i+1:2}. {importance_df.iloc[i]['Feature']:<20}: {importance_df.iloc[i]['Importance']:.4f}")
elif hasattr(best_model, 'coef_'):
    coef_df = pd.DataFrame({
        'Feature': feature_cols,
        'Coefficient': abs(best_model.coef_)
    }).sort_values('Coefficient', ascending=False)
    
    print("\n   Top 10 Most Important Features (by coefficient):")
    for i in range(min(10, len(coef_df))):
        print(f"   {i+1:2}. {coef_df.iloc[i]['Feature']:<20}: {coef_df.iloc[i]['Coefficient']:.4f}")
else:
    print_warning("Feature importance not available for this model")

# Step 8: Save all models and artifacts
print_header("💾 SAVING MODELS")

# Save best model
joblib.dump(best_model, 'models/best_model.pkl')
print_success("best_model.pkl saved")

# Save all models
all_models = {name: res['model'] for name, res in results.items()}
joblib.dump(all_models, 'models/all_models.pkl')
print_success("all_models.pkl saved")

# Save feature columns
joblib.dump(feature_cols, 'models/feature_columns.pkl')
print_success("feature_columns.pkl saved")

# Save results
results_df.to_csv('models/model_results.csv')
print_success("model_results.csv saved")

# Save preprocessor info
preprocessor_info = {
    'feature_cols': feature_cols,
    'n_features': len(feature_cols),
    'n_samples': len(df),
    'target_mean': y.mean(),
    'target_std': y.std()
}
joblib.dump(preprocessor_info, 'models/preprocessor.pkl')
print_success("preprocessor.pkl saved")

# Save price classifier
price_classifier = {
    'classify': classify_price,
    'get_emoji': get_price_emoji,
    'budget_threshold': 40,
    'affordable_threshold': 70,
    'mid_threshold': 120,
    'premium_threshold': 200
}
joblib.dump(price_classifier, 'models/price_classifier.pkl')
print_success("price_classifier.pkl saved")

# Step 9: Build recommendation system
print_header("🎯 BUILDING RECOMMENDATION SYSTEM")

try:
    from sklearn.neighbors import NearestNeighbors
    from sklearn.preprocessing import MinMaxScaler
    
    # Use numerical features for recommendation
    rec_features = ['total_sqft', 'bath', 'balcony', 'bhk']
    if 'price_per_sqft' in df.columns:
        rec_features.append('price_per_sqft')
    if 'price' in df.columns:
        rec_features.append('price')
    
    # Only use features that exist
    rec_features = [f for f in rec_features if f in df.columns]
    
    print_info(f"Using features for recommendation: {rec_features}")
    
    # Prepare data for KNN
    rec_data = df[rec_features].fillna(df[rec_features].median())
    scaler = MinMaxScaler()
    rec_data_scaled = scaler.fit_transform(rec_data)
    
    # Train KNN
    knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
    knn.fit(rec_data_scaled)
    
    # Save recommendation model
    recommendation_model = {
        'knn': knn,
        'scaler': scaler,
        'features': rec_features,
        'sample_data': df[['price', 'total_sqft', 'bhk'] + rec_features].head(1000).to_dict()
    }
    joblib.dump(recommendation_model, 'models/recommendation_model.pkl')
    print_success("recommendation_model.pkl saved")
    
except Exception as e:
    print_warning(f"Recommendation system error: {e}")
    # Create fallback recommendation model
    fallback_model = {
        'knn': None,
        'scaler': None,
        'features': rec_features if 'rec_features' in dir() else ['total_sqft', 'bhk'],
        'error': str(e)
    }
    joblib.dump(fallback_model, 'models/recommendation_model.pkl')
    print_warning("Fallback recommendation model saved")

# Step 10: Final Summary
print_header("✅ TRAINING COMPLETE!")

print_info(f"Dataset: {len(df)} properties, {len(feature_cols)} features")
print_info(f"Best Model: {best_model_name}")
print_metric("   R² Score", f"{results_df.loc[best_model_name, 'R² Score']:.4f}")
print_metric("   MAE", f"{results_df.loc[best_model_name, 'MAE (Lakhs)']:.2f} Lakhs")

print("\n📁 Saved Files in 'models/' folder:")
saved_files = []
for file in os.listdir('models'):
    if file.endswith('.pkl') or file.endswith('.csv'):
        size = os.path.getsize(f'models/{file}') / 1024
        saved_files.append(f"   • {file:<30} ({size:6.1f} KB)")

for f in saved_files:
    print(f)

print_header("🎉 You can now run: streamlit run app.py")
print("   Or test recommendation: python scripts/test_recommendation.py")
print_header("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")