import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
import joblib
import os
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# ==================== PRICE CATEGORY DEFINITIONS ====================
PRICE_CATEGORIES = {
    0: {'name': 'Budget', 'range': '< 40 Lakhs', 'emoji': '🟢', 'color': '#28a745', 'description': 'Affordable homes perfect for first-time buyers'},
    1: {'name': 'Affordable', 'range': '40-70 Lakhs', 'emoji': '🟡', 'color': '#ffc107', 'description': 'Good value properties in developing areas'},
    2: {'name': 'Mid-Range', 'range': '70-120 Lakhs', 'emoji': '🟠', 'color': '#fd7e14', 'description': 'Well-balanced properties in prime locations'},
    3: {'name': 'Premium', 'range': '120-200 Lakhs', 'emoji': '🔴', 'color': '#dc3545', 'description': 'Luxury properties with premium amenities'},
    4: {'name': 'Luxury', 'range': '> 200 Lakhs', 'emoji': '💎', 'color': '#8B5CF6', 'description': 'Ultra-premium properties in elite neighborhoods'}
}

# Reverse mapping for price ranges
PRICE_TO_CATEGORY = [
    (40, 0),   # < 40 Lakhs -> Budget
    (70, 1),   # 40-70 Lakhs -> Affordable
    (120, 2),  # 70-120 Lakhs -> Mid-Range
    (200, 3),  # 120-200 Lakhs -> Premium
    (float('inf'), 4)  # > 200 Lakhs -> Luxury
]

class PriceClassifier:
    """
    Classify properties into price categories using ML
    Supports 5 price tiers: Budget, Affordable, Mid-Range, Premium, Luxury
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols = None
        self.is_trained = False
        
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features for price classification
        """
        features = pd.DataFrame()
        
        # Basic property features
        features['total_sqft'] = df['total_sqft']
        features['bhk'] = df['bhk']
        features['bath'] = df['bath'] if 'bath' in df.columns else df['bhk']
        features['balcony'] = df['balcony'] if 'balcony' in df.columns else 1
        
        # Derived features
        features['sqft_per_bhk'] = df['total_sqft'] / df['bhk']
        features['rooms_per_bhk'] = (df['bhk'] + (df['bath'] if 'bath' in df.columns else df['bhk'])) / df['bhk']
        
        # Location features (if available)
        if 'location' in df.columns:
            # Create location frequency encoding
            location_counts = df['location'].value_counts()
            features['location_popularity'] = df['location'].map(location_counts) / len(df)
            features['location_popularity'] = features['location_popularity'].fillna(0)
        
        # Area type features (if available)
        if 'area_type' in df.columns:
            area_type_map = {'Premium': 3, 'Mid-range': 2, 'Developing': 1}
            features['area_type_score'] = df['area_type'].map(area_type_map).fillna(2)
        else:
            features['area_type_score'] = 2
        
        # Amenity score (if available)
        if 'amenity_score' in df.columns:
            features['amenity_score'] = df['amenity_score']
        else:
            features['amenity_score'] = 3.5
        
        # Price per sqft
        if 'price' in df.columns:
            features['price_per_sqft'] = df['price'] / df['total_sqft']
        
        return features
    
    def create_labels(self, df: pd.DataFrame) -> np.ndarray:
        """
        Create price category labels from price values
        Returns array of category indices (0-4)
        """
        prices = df['price'].values
        labels = np.zeros(len(prices), dtype=int)
        
        for i, price in enumerate(prices):
            for threshold, category in PRICE_TO_CATEGORY:
                if price < threshold:
                    labels[i] = category
                    break
        
        return labels
    
    def train(self, X: pd.DataFrame, y: np.ndarray = None, df: pd.DataFrame = None) -> 'PriceClassifier':
        """
        Train the price classifier
        Can accept either (X, y) or (df) where y is derived from price column
        """
        if df is not None:
            # Extract features and labels from dataframe
            X = self.extract_features(df)
            y = self.create_labels(df)
            self.feature_cols = X.columns.tolist()
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train classifier
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y)
        
        # Calculate cross-validation score
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)
        print(f"✅ Price classifier trained with CV accuracy: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        self.is_trained = True
        
        # Save model
        self.save_models()
        
        return self
    
    def predict(self, features: Dict[str, Any] or pd.DataFrame) -> Dict:
        """
        Predict price category for given features
        Returns dictionary with category details
        """
        if not self.is_trained:
            self.load_models()
        
        # Convert features to dataframe if dictionary
        if isinstance(features, dict):
            features_df = pd.DataFrame([features])
        else:
            features_df = features
        
        # Ensure all required feature columns are present
        if self.feature_cols:
            for col in self.feature_cols:
                if col not in features_df.columns:
                    features_df[col] = 0
            features_df = features_df[self.feature_cols]
        
        # Scale features
        features_scaled = self.scaler.transform(features_df)
        
        # Predict category
        prediction = self.model.predict(features_scaled)[0]
        
        # Get probabilities
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Get category details
        category_info = PRICE_CATEGORIES.get(prediction, PRICE_CATEGORIES[2])
        
        return {
            'category_id': int(prediction),
            'category_name': category_info['name'],
            'category_range': category_info['range'],
            'category_emoji': category_info['emoji'],
            'category_color': category_info['color'],
            'category_description': category_info['description'],
            'confidence': float(max(probabilities)),
            'probabilities': {
                PRICE_CATEGORIES[i]['name']: float(probabilities[i]) 
                for i in range(len(probabilities))
            }
        }
    
    def predict_proba(self, features: Dict[str, Any] or pd.DataFrame) -> Dict[str, float]:
        """
        Get probability distribution across all price categories
        """
        if not self.is_trained:
            self.load_models()
        
        # Convert features to dataframe if dictionary
        if isinstance(features, dict):
            features_df = pd.DataFrame([features])
        else:
            features_df = features
        
        # Ensure all required feature columns are present
        if self.feature_cols:
            for col in self.feature_cols:
                if col not in features_df.columns:
                    features_df[col] = 0
            features_df = features_df[self.feature_cols]
        
        # Scale features
        features_scaled = self.scaler.transform(features_df)
        
        # Get probabilities
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        return {
            PRICE_CATEGORIES[i]['name']: float(probabilities[i])
            for i in range(len(probabilities))
        }
    
    def save_models(self):
        """Save the trained model and scaler"""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/price_classifier.pkl')
        joblib.dump(self.scaler, 'models/price_classifier_scaler.pkl')
        joblib.dump(self.feature_cols, 'models/price_classifier_features.pkl')
        print("✅ Price classifier models saved")
    
    def load_models(self):
        """Load the trained model and scaler"""
        try:
            self.model = joblib.load('models/price_classifier.pkl')
            self.scaler = joblib.load('models/price_classifier_scaler.pkl')
            self.feature_cols = joblib.load('models/price_classifier_features.pkl')
            self.is_trained = True
            print("✅ Price classifier models loaded")
        except FileNotFoundError:
            print("⚠️ Price classifier models not found. Please train first.")
            self.is_trained = False
        except Exception as e:
            print(f"⚠️ Error loading price classifier: {e}")
            self.is_trained = False
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from the trained model"""
        if not self.is_trained or self.model is None:
            return pd.DataFrame()
        
        if self.feature_cols and hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_cols,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            return importance_df
        return pd.DataFrame()

def classify_price_range(price: float) -> Dict:
    """
    Classify price into category based on price value
    (Rule-based classification without ML)
    """
    for threshold, category_id in PRICE_TO_CATEGORY:
        if price < threshold:
            category_info = PRICE_CATEGORIES[category_id]
            return {
                'category_id': category_id,
                'category_name': category_info['name'],
                'category_range': category_info['range'],
                'category_emoji': category_info['emoji'],
                'category_color': category_info['color'],
                'category_description': category_info['description']
            }
    
    # Default to Luxury
    return PRICE_CATEGORIES[4].copy()

def get_price_trend(
    df: pd.DataFrame, 
    location: str = None, 
    bhk: int = None
) -> Dict:
    """
    Analyze price trends for a location or overall market
    """
    # Filter data
    filtered_df = df.copy()
    if location:
        filtered_df = filtered_df[filtered_df['location'] == location]
    if bhk:
        filtered_df = filtered_df[filtered_df['bhk'] == bhk]
    
    if len(filtered_df) < 5:
        return {
            'trend': 'insufficient_data',
            'message': 'Not enough data for trend analysis',
            'avg_price': None,
            'price_range': None
        }
    
    # Calculate statistics
    avg_price = filtered_df['price'].mean()
    median_price = filtered_df['price'].median()
    min_price = filtered_df['price'].min()
    max_price = filtered_df['price'].max()
    std_price = filtered_df['price'].std()
    
    # Calculate percentile distribution
    percentiles = {
        'p25': filtered_df['price'].quantile(0.25),
        'p50': filtered_df['price'].quantile(0.50),
        'p75': filtered_df['price'].quantile(0.75),
        'p90': filtered_df['price'].quantile(0.90)
    }
    
    # Determine category distribution
    category_counts = {name: 0 for name in ['Budget', 'Affordable', 'Mid-Range', 'Premium', 'Luxury']}
    for price in filtered_df['price']:
        category = classify_price_range(price)['category_name']
        category_counts[category] += 1
    
    # Find most common category
    most_common_category = max(category_counts, key=category_counts.get)
    
    return {
        'trend': 'stable',  # Would need time series data for actual trend
        'message': f"Analysis based on {len(filtered_df)} properties",
        'avg_price': round(avg_price, 2),
        'median_price': round(median_price, 2),
        'price_range': (round(min_price, 2), round(max_price, 2)),
        'std_price': round(std_price, 2),
        'percentiles': {k: round(v, 2) for k, v in percentiles.items()},
        'category_distribution': category_counts,
        'most_common_category': most_common_category,
        'sample_size': len(filtered_df)
    }

def compare_with_market(
    predicted_price: float,
    location: str,
    bhk: int,
    df: pd.DataFrame
) -> Dict:
    """
    Compare predicted price with market average
    """
    # Get market data for similar properties
    similar = df[(df['location'] == location) & (df['bhk'] == bhk)]
    
    if len(similar) < 3:
        return {
            'comparison': 'insufficient_data',
            'message': 'Not enough similar properties for comparison',
            'market_avg': None,
            'difference_percent': None
        }
    
    market_avg = similar['price'].mean()
    difference = predicted_price - market_avg
    difference_percent = (difference / market_avg) * 100
    
    # Determine comparison result
    if difference_percent > 15:
        comparison = 'significantly_above'
        message = f"Predicted price is {difference_percent:.1f}% ABOVE market average"
    elif difference_percent > 5:
        comparison = 'slightly_above'
        message = f"Predicted price is {difference_percent:.1f}% above market average"
    elif difference_percent < -15:
        comparison = 'significantly_below'
        message = f"Predicted price is {abs(difference_percent):.1f}% BELOW market average"
    elif difference_percent < -5:
        comparison = 'slightly_below'
        message = f"Predicted price is {abs(difference_percent):.1f}% below market average"
    else:
        comparison = 'market_rate'
        message = "Predicted price is in line with market average"
    
    # Get market price category
    market_category = classify_price_range(market_avg)
    
    return {
        'comparison': comparison,
        'message': message,
        'market_avg': round(market_avg, 2),
        'difference': round(difference, 2),
        'difference_percent': round(difference_percent, 1),
        'market_category': market_category['category_name'],
        'similar_properties_count': len(similar),
        'price_range': (round(similar['price'].min(), 2), round(similar['price'].max(), 2))
    }

def create_price_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add price category column to dataframe
    """
    df = df.copy()
    df['price_category'] = df['price'].apply(
        lambda x: classify_price_range(x)['category_id']
    )
    df['price_category_name'] = df['price_category'].map(
        lambda x: PRICE_CATEGORIES[x]['name']
    )
    return df

# ==================== MAIN EXPORTS ====================
__all__ = [
    'PriceClassifier',
    'classify_price_range',
    'get_price_trend',
    'compare_with_market',
    'create_price_categories',
    'PRICE_CATEGORIES',
    'PRICE_TO_CATEGORY'
]

if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("🏷️ PRICE CLASSIFIER MODULE TEST")
    print("=" * 60)
    
    # Test price classification
    test_prices = [35, 55, 95, 150, 250]
    for price in test_prices:
        result = classify_price_range(price)
        print(f"Price: ₹{price}L → {result['category_emoji']} {result['category_name']} ({result['category_range']})")
    
    print("\n✅ Price classifier module ready!")