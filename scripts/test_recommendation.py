"""
SmartEstate - Test Recommendation System
Tests KNN-based property recommendations with comprehensive scenarios
"""

import pandas as pd
import numpy as np
import joblib
import os
import sys
from datetime import datetime

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
    UNDERLINE = '\033[4m'

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

def print_value(label, value, unit=""):
    print(f"   {Colors.BOLD}{label}:{Colors.ENDC} {Colors.GREEN}{value}{unit}{Colors.ENDC}")

# ==================== PRICE CLASSIFICATION ====================
def classify_price(price):
    """Classify price into categories"""
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
    """Get emoji based on price category"""
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

# ==================== LOAD DATA ====================
def load_data():
    """Load dataset and models"""
    print_header("📂 LOADING DATA AND MODELS")
    
    # Check if processed data exists
    if os.path.exists('data/processed_data.csv'):
        df = pd.read_csv('data/processed_data.csv')
        print_success(f"Loaded processed data: {len(df)} properties")
    elif os.path.exists('data/Bengaluru_House_Data.csv'):
        df = pd.read_csv('data/Bengaluru_House_Data.csv')
        print_success(f"Loaded raw data: {len(df)} properties")
    else:
        print_warning("No dataset found. Creating sample data...")
        df = create_sample_data()
    
    # Load feature columns
    try:
        feature_cols = joblib.load('models/feature_columns.pkl')
        print_success(f"Loaded {len(feature_cols)} feature columns")
    except:
        print_warning("Feature columns not found, using default features")
        feature_cols = ['total_sqft', 'bhk', 'bath', 'balcony', 'price_per_sqft']
    
    # Load recommendation model
    try:
        rec_model = joblib.load('models/recommendation_model.pkl')
        if isinstance(rec_model, dict):
            knn = rec_model.get('knn')
            scaler = rec_model.get('scaler')
            rec_features = rec_model.get('features', feature_cols)
        else:
            knn = rec_model
            scaler = None
            rec_features = feature_cols
        print_success("Loaded recommendation model")
    except:
        print_warning("Recommendation model not found, using fallback")
        knn = None
        scaler = None
        rec_features = feature_cols
    
    return df, feature_cols, knn, scaler, rec_features

def create_sample_data():
    """Create sample data for testing"""
    np.random.seed(42)
    
    locations = [
        'Indiranagar', 'Koramangala', 'Whitefield', 'HSR Layout', 'Jayanagar',
        'Electronic City', 'BTM Layout', 'JP Nagar', 'Banashankari', 'Malleshwaram',
        'Rajajinagar', 'Hebbal', 'Yelahanka', 'RR Nagar', 'Vijayanagar'
    ]
    
    data = []
    for loc in locations:
        for _ in range(np.random.randint(20, 60)):
            total_sqft = np.random.uniform(500, 3000)
            bhk = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.30, 0.40, 0.20, 0.05])
            bath = min(bhk + np.random.randint(0, 2), 5)
            balcony = np.random.choice([0, 1, 2, 3], p=[0.1, 0.35, 0.35, 0.2])
            
            # Price based on location
            location_factors = {
                'Indiranagar': 2.5, 'Koramangala': 2.4, 'Jayanagar': 2.2,
                'Whitefield': 1.8, 'HSR Layout': 2.0, 'Electronic City': 1.5
            }
            factor = location_factors.get(loc, 1.2)
            price = (total_sqft / 1000) * 50 * factor + bhk * 15 + bath * 5 + balcony * 3
            price = max(20, min(500, round(price, 2)))
            
            data.append({
                'location': loc,
                'total_sqft': round(total_sqft, 2),
                'bhk': bhk,
                'bath': bath,
                'balcony': balcony,
                'price': price,
                'price_per_sqft': round(price / total_sqft * 100, 2)
            })
    
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/processed_data.csv', index=False)
    print_success(f"Created sample data with {len(df)} properties")
    return df

# ==================== DEMO 1: PRICE DISTRIBUTION ====================
def demo_price_distribution(df):
    """Show price distribution by category"""
    print_header("📊 DEMO 1: PRICE DISTRIBUTION BY CATEGORY")
    
    df['price_category'] = df['price'].apply(classify_price)
    df['price_emoji'] = df['price'].apply(get_price_emoji)
    
    category_stats = df['price_category'].value_counts()
    for category in ['Budget', 'Affordable', 'Mid-Range', 'Premium', 'Luxury']:
        count = category_stats.get(category, 0)
        pct = count / len(df) * 100
        bar = '█' * int(pct / 2)
        print(f"   {get_price_emoji(0)} {category:<12}: {count:4} ({pct:5.1f}%) {bar}")
    
    print_info(f"Total properties: {len(df)}")

# ==================== DEMO 2: BEST VALUE PROPERTIES ====================
def demo_best_value(df):
    """Show best value properties (lowest price per sqft)"""
    print_header("🏆 DEMO 2: BEST VALUE PROPERTIES")
    
    best_value = df.nsmallest(10, 'price_per_sqft')
    
    print("\n   Top 10 Best Value Properties (Lowest Price per Sqft):")
    print("   " + "-" * 65)
    for i, (idx, row) in enumerate(best_value.iterrows(), 1):
        category = classify_price(row['price'])
        emoji = get_price_emoji(row['price'])
        location = row.get('location', 'Unknown')
        print(f"   {i:2}. {emoji} {category:<10} | ₹{row['price']:6.1f}L | {row['total_sqft']:6.0f} sqft | ₹{row['price_per_sqft']:6.2f}/sqft | {location[:20]}")

# ==================== DEMO 3: STATISTICS BY BHK ====================
def demo_stats_by_bhk(df):
    """Show price statistics by BHK"""
    print_header("🏠 DEMO 3: PRICE STATISTICS BY BHK")
    
    for bhk in [1, 2, 3, 4, 5]:
        subset = df[df['bhk'] == bhk]
        if len(subset) > 0:
            print(f"\n   {bhk} BHK Properties ({len(subset)} total):")
            print(f"      Avg Price:    ₹{subset['price'].mean():8.1f} Lakhs")
            print(f"      Price Range:  ₹{subset['price'].min():6.1f} - ₹{subset['price'].max():6.1f} Lakhs")
            print(f"      Avg Area:     {subset['total_sqft'].mean():8.0f} sqft")
            print(f"      Avg Price/sqft: ₹{subset['price_per_sqft'].mean():6.2f}")

# ==================== DEMO 4: STATISTICS BY CATEGORY ====================
def demo_stats_by_category(df):
    """Show price statistics by category"""
    print_header("💰 DEMO 4: PRICE STATISTICS BY CATEGORY")
    
    for category in ['Budget', 'Affordable', 'Mid-Range', 'Premium', 'Luxury']:
        subset = df[df['price_category'] == category]
        if len(subset) > 0:
            emoji = get_price_emoji(subset['price'].iloc[0])
            print(f"\n   {emoji} {category} Properties ({len(subset)} total):")
            print(f"      Avg Price:      ₹{subset['price'].mean():8.1f} Lakhs")
            print(f"      Avg Area:       {subset['total_sqft'].mean():8.0f} sqft")
            print(f"      Avg Price/sqft: ₹{subset['price_per_sqft'].mean():6.2f}")

# ==================== DEMO 5: KNN RECOMMENDATIONS ====================
def demo_knn_recommendations(df, knn, scaler, rec_features):
    """Show KNN-based property recommendations"""
    print_header("🎯 DEMO 5: KNN PROPERTY RECOMMENDATIONS")
    
    if knn is None:
        print_warning("KNN model not available, skipping...")
        return
    
    # Pick a random property
    np.random.seed(42)
    sample_idx = np.random.randint(0, len(df))
    sample_property = df.iloc[sample_idx]
    
    print(f"\n   🔍 Reference Property:")
    print(f"      Location: {sample_property.get('location', 'Unknown')}")
    print(f"      Price: ₹{sample_property['price']:.1f}L ({classify_price(sample_property['price'])})")
    print(f"      BHK: {sample_property['bhk']} | Area: {sample_property['total_sqft']:.0f} sqft")
    print(f"      Bath: {sample_property['bath']} | Balcony: {sample_property['balcony']}")
    print(f"      Price/sqft: ₹{sample_property['price_per_sqft']:.2f}")
    
    # Get similar properties
    try:
        sample_features = df[rec_features].iloc[sample_idx].values.reshape(1, -1)
        
        if scaler:
            sample_scaled = scaler.transform(sample_features)
        else:
            sample_scaled = sample_features
        
        distances, indices = knn.kneighbors(sample_scaled, n_neighbors=6)
        
        print(f"\n   ✅ Similar Properties (KNN Recommendations):")
        print("   " + "-" * 70)
        for i, idx in enumerate(indices[0][1:], 1):
            prop = df.iloc[idx]
            emoji = get_price_emoji(prop['price'])
            print(f"\n   {i}. {emoji} {classify_price(prop['price']):<10} | ₹{prop['price']:6.1f}L")
            print(f"      {prop['bhk']} BHK | {prop['total_sqft']:.0f} sqft | Bath: {prop['bath']} | Balcony: {prop['balcony']}")
            print(f"      Price/sqft: ₹{prop['price_per_sqft']:.2f} | Similarity: {distances[0][i]:.4f}")
    except Exception as e:
        print_warning(f"KNN recommendation failed: {e}")

# ==================== DEMO 6: BUDGET + BHK RECOMMENDATIONS ====================
def demo_budget_bhk_recommendations(df):
    """Recommend properties by budget and BHK"""
    print_header("💰 DEMO 6: RECOMMENDATIONS BY BUDGET + BHK")
    
    # Test scenarios
    scenarios = [
        {"budget": 50, "bhk": 2, "name": "Budget 50L, 2 BHK"},
        {"budget": 80, "bhk": 3, "name": "Budget 80L, 3 BHK"},
        {"budget": 120, "bhk": 3, "name": "Budget 120L, 3 BHK"},
        {"budget": 200, "bhk": 4, "name": "Budget 200L, 4 BHK"}
    ]
    
    for scenario in scenarios:
        budget = scenario["budget"]
        bhk = scenario["bhk"]
        name = scenario["name"]
        
        filtered = df[(df['price'] <= budget) & (df['bhk'] == bhk)]
        filtered = filtered.nsmallest(5, 'price')
        
        print(f"\n   🏠 {name}:")
        if len(filtered) > 0:
            for i, (idx, row) in enumerate(filtered.iterrows(), 1):
                emoji = get_price_emoji(row['price'])
                location = row.get('location', 'Unknown')
                print(f"      {i}. {emoji} ₹{row['price']:6.1f}L | {row['total_sqft']:6.0f} sqft | {row['bhk']} BHK | {location[:20]}")
        else:
            print(f"      No properties found")

# ==================== DEMO 7: PRICE RANGE RECOMMENDATIONS ====================
def demo_price_range_recommendations(df):
    """Recommend best value properties in price range"""
    print_header("📈 DEMO 7: BEST VALUE IN PRICE RANGE")
    
    price_ranges = [
        {"min": 30, "max": 60, "name": "₹30L - ₹60L"},
        {"min": 60, "max": 100, "name": "₹60L - ₹100L"},
        {"min": 100, "max": 150, "name": "₹100L - ₹150L"},
        {"min": 150, "max": 250, "name": "₹150L - ₹250L"}
    ]
    
    for pr in price_ranges:
        min_price = pr["min"]
        max_price = pr["max"]
        name = pr["name"]
        
        filtered = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
        filtered = filtered.nsmallest(5, 'price_per_sqft')
        
        print(f"\n   📍 {name}:")
        if len(filtered) > 0:
            for i, (idx, row) in enumerate(filtered.iterrows(), 1):
                emoji = get_price_emoji(row['price'])
                location = row.get('location', 'Unknown')
                print(f"      {i}. {emoji} ₹{row['price']:6.1f}L | {row['total_sqft']:6.0f} sqft | ₹{row['price_per_sqft']:5.2f}/sqft | {location[:20]}")
        else:
            print(f"      No properties found")

# ==================== DEMO 8: TOP LOCATIONS ====================
def demo_top_locations(df):
    """Show top locations by average price"""
    print_header("📍 DEMO 8: TOP LOCATIONS BY AVERAGE PRICE")
    
    if 'location' not in df.columns:
        print_warning("Location column not found")
        return
    
    location_stats = df.groupby('location').agg({
        'price': ['mean', 'count', 'min', 'max'],
        'total_sqft': 'mean'
    }).round(2)
    
    location_stats.columns = ['avg_price', 'count', 'min_price', 'max_price', 'avg_sqft']
    location_stats = location_stats.sort_values('avg_price', ascending=False)
    
    print("\n   Top 10 Most Expensive Locations:")
    print("   " + "-" * 70)
    for i, (loc, row) in enumerate(location_stats.head(10).iterrows(), 1):
        emoji = get_price_emoji(row['avg_price'])
        print(f"   {i:2}. {emoji} {loc:<20} | ₹{row['avg_price']:6.1f}L | {row['count']:3} props | {row['avg_sqft']:.0f} sqft")
    
    print("\n   Top 10 Most Affordable Locations:")
    print("   " + "-" * 70)
    for i, (loc, row) in enumerate(location_stats.tail(10).iterrows(), 1):
        emoji = get_price_emoji(row['avg_price'])
        print(f"   {i:2}. {emoji} {loc:<20} | ₹{row['avg_price']:6.1f}L | {row['count']:3} props | {row['avg_sqft']:.0f} sqft")

# ==================== DEMO 9: INVESTMENT OPPORTUNITIES ====================
def demo_investment_opportunities(df):
    """Identify potential investment opportunities"""
    print_header("💎 DEMO 9: INVESTMENT OPPORTUNITIES")
    
    # Properties with good value (low price per sqft but reasonable total price)
    investment_candidates = df[
        (df['price_per_sqft'] < df['price_per_sqft'].quantile(0.3)) &
        (df['price'] < df['price'].quantile(0.7))
    ].nsmallest(10, 'price_per_sqft')
    
    print("\n   🔥 Top 10 Investment Opportunities (Good Value):")
    print("   " + "-" * 70)
    for i, (idx, row) in enumerate(investment_candidates.iterrows(), 1):
        emoji = get_price_emoji(row['price'])
        location = row.get('location', 'Unknown')
        print(f"   {i:2}. {emoji} {location:<20} | ₹{row['price']:6.1f}L | {row['total_sqft']:.0f} sqft")
        print(f"        Price/sqft: ₹{row['price_per_sqft']:.2f} | {row['bhk']} BHK | {row['bath']} Bath")

# ==================== MAIN FUNCTION ====================
def main():
    """Main test function"""
    print_header("🎯 SMARTESTATE - RECOMMENDATION SYSTEM DEMO")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data and models
    df, feature_cols, knn, scaler, rec_features = load_data()
    
    # Add price category
    df['price_category'] = df['price'].apply(classify_price)
    
    # Run all demos
    demo_price_distribution(df)
    demo_best_value(df)
    demo_stats_by_bhk(df)
    demo_stats_by_category(df)
    demo_knn_recommendations(df, knn, scaler, rec_features)
    demo_budget_bhk_recommendations(df)
    demo_price_range_recommendations(df)
    demo_top_locations(df)
    demo_investment_opportunities(df)
    
    # Print summary
    print_header("📁 MODELS SUMMARY")
    if os.path.exists('models'):
        model_files = [f for f in os.listdir('models') if f.endswith('.pkl')]
        for file in model_files[:10]:
            size = os.path.getsize(f'models/{file}') / 1024
            print(f"   • {file:<35} ({size:6.1f} KB)")
        if len(model_files) > 10:
            print(f"   ... and {len(model_files) - 10} more files")
    
    print_header("✅ RECOMMENDATION SYSTEM TEST COMPLETE!")

if __name__ == "__main__":
    main()