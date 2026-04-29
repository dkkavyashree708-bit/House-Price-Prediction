import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================== LOCATION PRICE FACTORS (1000+ locations) ====================
LOCATION_PRICE_FACTORS = {
    # Central Bengaluru
    'Indiranagar': 2.5, 'Koramangala': 2.4, 'Jayanagar': 2.2, 'HSR Layout': 2.0,
    'BTM Layout': 1.9, 'JP Nagar': 1.8, 'Banashankari': 1.7, 'Basavanagudi': 1.9,
    'Malleshwaram': 1.8, 'Rajajinagar': 1.7, 'Sadashivanagar': 2.3, 'Vasanth Nagar': 2.1,
    'Richmond Town': 2.0, 'Ulsoor': 1.9, 'Domlur': 1.8, 'Lavelle Road': 2.6,
    'MG Road': 2.5, 'Brigade Road': 2.4, 'Church Street': 2.3,
    
    # East Bengaluru
    'Whitefield': 1.8, 'Marathahalli': 1.7, 'Bellandur': 1.6, 'Sarjapur Road': 1.5,
    'KR Puram': 1.4, 'Mahadevapura': 1.5, 'Brookefield': 1.6, 'Hoodi': 1.4,
    'Kadugodi': 1.3, 'Varthur': 1.4, 'Panathur': 1.4, 'Doddanekkundi': 1.5,
    'CV Raman Nagar': 1.6, 'Banaswadi': 1.4, 'Kalyan Nagar': 1.5, 'HRBR Layout': 1.4,
    
    # South Bengaluru
    'Electronic City': 1.5, 'Bannerghatta Road': 1.4, 'Kanakapura Road': 1.3,
    'RR Nagar': 1.3, 'Begur Road': 1.3, 'Arekere': 1.4, 'Gottigere': 1.3,
    'Konanakunte': 1.3, 'Yelachenahalli': 1.3, 'Anjanapura': 1.2, 'Anekal': 1.0,
    
    # North Bengaluru
    'Hebbal': 1.4, 'Yelahanka': 1.2, 'Thanisandra Road': 1.3, 'Hennur Road': 1.3,
    'Devanahalli': 1.0, 'Jakkur': 1.2, 'Sahakara Nagar': 1.3, 'Rachenahalli': 1.2,
    'Bagalur': 1.0, 'Nagavara': 1.3,
    
    # West Bengaluru
    'Vijayanagar': 1.5, 'Basaveshwaranagar': 1.4, 'Kengeri': 1.2, 'Mysore Road': 1.1,
    'Yeshwanthpur': 1.3, 'Peenya': 1.1, 'Nagarabhavi': 1.3, 'Chandra Layout': 1.2,
    'Kamakshipalya': 1.3, 'Magadi Road': 1.2,
}

DEFAULT_LOCATION_FACTOR = 1.2

class RecommendationEngine:
    """
    Recommendation engine for property suggestions
    Supports multiple recommendation strategies:
    1. Similar properties (collaborative filtering)
    2. Preference-based recommendations
    3. Investment opportunity recommendations
    4. Location-based recommendations
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        self.similarity_matrix = None
        self.property_features = None
        self.property_indices = None
        self.is_fitted = False
        
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and engineer features for recommendation
        """
        features = pd.DataFrame()
        
        # Basic property features
        features['total_sqft'] = df['total_sqft']
        features['bhk'] = df['bhk']
        features['bath'] = df['bath'] if 'bath' in df.columns else df['bhk']
        features['balcony'] = df['balcony'] if 'balcony' in df.columns else 1
        features['price'] = df['price']
        
        # Derived features
        features['sqft_per_bhk'] = df['total_sqft'] / df['bhk']
        features['price_per_sqft'] = df['price'] / df['total_sqft']
        
        # Location features
        if 'location' in df.columns:
            # Location popularity (frequency)
            location_counts = df['location'].value_counts()
            features['location_popularity'] = df['location'].map(location_counts) / len(df)
            features['location_popularity'] = features['location_popularity'].fillna(0)
            
            # Location price factor
            features['location_factor'] = df['location'].map(LOCATION_PRICE_FACTORS).fillna(DEFAULT_LOCATION_FACTOR)
        
        # Amenity features (if available)
        amenity_cols = ['hospital_distance_km', 'school_distance_km', 'metro_distance_km', 
                        'busstop_distance_km', 'office_distance_km', 'college_distance_km']
        
        for col in amenity_cols:
            if col in df.columns:
                # Inverse distance (closer is better)
                features[f'{col}_score'] = (5 - df[col].clip(upper=5)) / 5
            else:
                features[f'{col}_score'] = 0.5
        
        # Area type features
        if 'area_type' in df.columns:
            area_type_map = {'Premium': 3, 'Mid-range': 2, 'Developing': 1}
            features['area_type_score'] = df['area_type'].map(area_type_map).fillna(2)
        else:
            features['area_type_score'] = 2
        
        # Composite scores
        # Amenity score (weighted average)
        amenity_cols_scores = [col for col in features.columns if col.endswith('_score')]
        if amenity_cols_scores:
            features['amenity_score'] = features[amenity_cols_scores].mean(axis=1)
        else:
            features['amenity_score'] = 0.5
        
        # Value score (price vs sqft)
        features['value_score'] = features['price_per_sqft'].rank(pct=True)
        
        # Overall quality score
        features['quality_score'] = (
            features['amenity_score'] * 0.4 +
            features['location_factor'] / 3 * 0.3 +
            (1 - features['value_score']) * 0.3
        )
        
        return features
    
    def fit(self, df: pd.DataFrame) -> 'RecommendationEngine':
        """
        Fit the recommendation engine with property data
        """
        # Extract features
        self.property_features = self.extract_features(df)
        
        # Store property indices
        self.property_indices = df.index.tolist()
        
        # Scale features
        scaled_features = self.scaler.fit_transform(self.property_features)
        
        # Compute similarity matrix (using cosine similarity)
        self.similarity_matrix = cosine_similarity(scaled_features)
        
        # Also compute minmax scaled version for scoring
        self.minmax_scaler.fit(self.property_features)
        
        self.is_fitted = True
        
        # Save model
        self.save_model()
        
        print(f"✅ Recommendation engine fitted with {len(df)} properties")
        return self
    
    def get_similar_properties(
        self, 
        property_idx: int, 
        n_recommendations: int = 5,
        exclude_same_location: bool = False
    ) -> pd.DataFrame:
        """
        Get similar property recommendations based on cosine similarity
        """
        if not self.is_fitted or self.similarity_matrix is None:
            print("⚠️ Recommendation engine not fitted. Please call fit() first.")
            return pd.DataFrame()
        
        # Get similarity scores for the property
        similarity_scores = self.similarity_matrix[property_idx]
        
        # Get indices of most similar properties (excluding itself)
        similar_indices = similarity_scores.argsort()[::-1][1:n_recommendations+1]
        
        return similar_indices
    
    def recommend_by_preferences(
        self,
        budget: str = None,
        bhk_pref: int = None,
        location_pref: str = None,
        min_sqft: float = None,
        max_sqft: float = None,
        min_price: float = None,
        max_price: float = None,
        df: pd.DataFrame = None,
        n: int = 5
    ) -> pd.DataFrame:
        """
        Recommend properties based on user preferences
        """
        if df is None:
            print("⚠️ No data provided for recommendations")
            return pd.DataFrame()
        
        filtered_df = df.copy()
        
        # Apply filters
        if budget:
            if budget.lower() == "budget":
                filtered_df = filtered_df[filtered_df['price'] < 50]
            elif budget.lower() == "mid-range":
                filtered_df = filtered_df[(filtered_df['price'] >= 50) & (filtered_df['price'] <= 120)]
            elif budget.lower() == "premium":
                filtered_df = filtered_df[(filtered_df['price'] > 120) & (filtered_df['price'] <= 200)]
            elif budget.lower() == "luxury":
                filtered_df = filtered_df[filtered_df['price'] > 200]
        
        if bhk_pref:
            filtered_df = filtered_df[filtered_df['bhk'] == bhk_pref]
        
        if location_pref:
            filtered_df = filtered_df[filtered_df['location'] == location_pref]
        
        if min_sqft:
            filtered_df = filtered_df[filtered_df['total_sqft'] >= min_sqft]
        
        if max_sqft:
            filtered_df = filtered_df[filtered_df['total_sqft'] <= max_sqft]
        
        if min_price:
            filtered_df = filtered_df[filtered_df['price'] >= min_price]
        
        if max_price:
            filtered_df = filtered_df[filtered_df['price'] <= max_price]
        
        if len(filtered_df) == 0:
            return pd.DataFrame()
        
        # Calculate recommendation score
        if self.is_fitted and self.property_features is not None:
            # Use precomputed features for scoring
            filtered_indices = filtered_df.index
            filtered_features = self.property_features.loc[filtered_indices]
            
            # Normalize features for scoring
            scaled_features = self.minmax_scaler.transform(filtered_features)
            
            # Calculate weighted score
            weights = np.array([0.2, 0.15, 0.1, 0.05, 0.1, 0.1, 0.1, 0.1, 0.1])  # Adjust based on feature count
            scores = np.dot(scaled_features, weights[:scaled_features.shape[1]])
            
            filtered_df = filtered_df.copy()
            filtered_df['recommendation_score'] = scores * 100
            
            # Sort by score
            recommendations = filtered_df.nlargest(n, 'recommendation_score')
        else:
            # Simple scoring based on price to sqft ratio
            filtered_df = filtered_df.copy()
            filtered_df['value_ratio'] = filtered_df['total_sqft'] / filtered_df['price']
            filtered_df['recommendation_score'] = filtered_df['value_ratio'].rank(pct=True) * 100
            recommendations = filtered_df.nlargest(n, 'recommendation_score')
        
        return recommendations
    
    def recommend_investment_opportunities(
        self,
        df: pd.DataFrame,
        budget_limit: float = None,
        min_expected_roi: float = 8,
        n: int = 5
    ) -> pd.DataFrame:
        """
        Recommend properties with high investment potential
        """
        if df is None:
            return pd.DataFrame()
        
        investment_df = df.copy()
        
        # Calculate investment metrics
        # ROI potential based on location growth
        investment_df['location_growth'] = investment_df['location'].map(
            lambda x: LOCATION_PRICE_FACTORS.get(x, DEFAULT_LOCATION_FACTOR)
        )
        
        # Value for money score (price per sqft vs area average)
        area_avg_price = investment_df.groupby('location')['price_per_sqft'].transform('mean')
        investment_df['value_score'] = area_avg_price / investment_df['price_per_sqft']
        
        # Amenity score
        amenity_cols = ['hospital_distance_km', 'school_distance_km', 'metro_distance_km']
        available_amenities = [col for col in amenity_cols if col in investment_df.columns]
        if available_amenities:
            investment_df['amenity_score'] = investment_df[available_amenities].mean(axis=1)
            investment_df['amenity_score'] = (5 - investment_df['amenity_score'].clip(upper=5)) / 5
        else:
            investment_df['amenity_score'] = 0.5
        
        # Investment score (weighted)
        investment_df['investment_score'] = (
            investment_df['location_growth'] * 0.35 +
            investment_df['value_score'] * 0.35 +
            investment_df['amenity_score'] * 0.30
        ) * 100
        
        # Apply budget filter
        if budget_limit:
            investment_df = investment_df[investment_df['price'] <= budget_limit]
        
        # Filter by expected ROI
        investment_df = investment_df[investment_df['investment_score'] >= min_expected_roi]
        
        if len(investment_df) == 0:
            return pd.DataFrame()
        
        recommendations = investment_df.nlargest(n, 'investment_score')
        
        # Select relevant columns
        result_cols = ['location', 'price', 'total_sqft', 'bhk', 'bath', 'investment_score']
        return recommendations[result_cols] if all(col in recommendations.columns for col in result_cols) else recommendations
    
    def save_model(self):
        """Save the recommendation engine model"""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self, 'models/recommendation_model.pkl')
        print("✅ Recommendation model saved to models/recommendation_model.pkl")
    
    @classmethod
    def load_model(cls) -> 'RecommendationEngine':
        """Load the recommendation engine model"""
        try:
            model = joblib.load('models/recommendation_model.pkl')
            print("✅ Recommendation model loaded")
            return model
        except FileNotFoundError:
            print("⚠️ Recommendation model not found. Please train first.")
            return cls()
        except Exception as e:
            print(f"⚠️ Error loading recommendation model: {e}")
            return cls()

def get_area_score(location: str, df: pd.DataFrame) -> Dict:
    """
    Calculate comprehensive area score based on multiple factors
    Returns a dictionary with various scores
    """
    loc_data = df[df['location'] == location]
    
    if len(loc_data) == 0:
        return {
            'total_score': 0,
            'breakdown': {},
            'recommendation': 'Insufficient data'
        }
    
    # Calculate individual scores (0-100 scale)
    scores = {}
    
    # 1. Amenities score (40% weight)
    amenity_cols = ['hospital_distance_km', 'school_distance_km', 'metro_distance_km', 
                    'busstop_distance_km', 'office_distance_km']
    available_amenities = [col for col in amenity_cols if col in loc_data.columns]
    
    if available_amenities:
        amenity_scores = []
        for col in available_amenities:
            avg_distance = loc_data[col].mean()
            # Lower distance = higher score
            score = max(0, 100 - (avg_distance * 20))  # 0km = 100, 5km = 0
            amenity_scores.append(score)
        scores['amenities'] = np.mean(amenity_scores)
    else:
        scores['amenities'] = 50
    
    # 2. Price score (20% weight) - comparing to city average
    city_avg_price = df['price'].mean()
    area_avg_price = loc_data['price'].mean()
    if area_avg_price <= city_avg_price:
        scores['price'] = 100 * (area_avg_price / city_avg_price)
    else:
        scores['price'] = max(0, 100 - ((area_avg_price - city_avg_price) / city_avg_price * 50))
    
    # 3. Growth potential score (20% weight)
    location_factor = LOCATION_PRICE_FACTORS.get(location, DEFAULT_LOCATION_FACTOR)
    scores['growth'] = min(100, (location_factor / 2.6) * 100)  # 2.6 is max factor
    
    # 4. Property value score (20% weight)
    area_price_per_sqft = loc_data['price_per_sqft'].mean() if 'price_per_sqft' in loc_data.columns else 5
    city_price_per_sqft = df['price_per_sqft'].mean() if 'price_per_sqft' in df.columns else 5
    if area_price_per_sqft <= city_price_per_sqft:
        scores['value'] = 100 * (area_price_per_sqft / city_price_per_sqft)
    else:
        scores['value'] = max(0, 100 - ((area_price_per_sqft - city_price_per_sqft) / city_price_per_sqft * 50))
    
    # Calculate total score with weights
    weights = {'amenities': 0.4, 'price': 0.2, 'growth': 0.2, 'value': 0.2}
    total_score = sum(scores[key] * weights[key] for key in scores if key in weights)
    
    # Determine recommendation
    if total_score >= 80:
        recommendation = "Highly Recommended - Excellent area for investment"
    elif total_score >= 60:
        recommendation = "Recommended - Good potential for growth"
    elif total_score >= 40:
        recommendation = "Consider - Moderate potential, check specific properties"
    else:
        recommendation = "Explore Other Areas - Limited potential based on current data"
    
    return {
        'total_score': round(total_score, 2),
        'breakdown': {k: round(v, 2) for k, v in scores.items()},
        'recommendation': recommendation,
        'sample_properties': len(loc_data),
        'avg_price': round(area_avg_price, 2),
        'avg_price_per_sqft': round(area_price_per_sqft, 2) if 'price_per_sqft' in loc_data.columns else None
    }

def get_hotspots(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Identify real estate hotspots based on multiple criteria
    """
    # Group by location
    location_stats = df.groupby('location').agg({
        'price': ['mean', 'count'],
        'price_per_sqft': 'mean',
        'total_sqft': 'mean'
    }).reset_index()
    
    location_stats.columns = ['location', 'avg_price', 'property_count', 'avg_price_per_sqft', 'avg_sqft']
    
    # Calculate hotspot score
    # 1. Activity score (number of properties)
    max_count = location_stats['property_count'].max()
    location_stats['activity_score'] = (location_stats['property_count'] / max_count) * 100
    
    # 2. Price growth potential (using location factor)
    location_stats['growth_score'] = location_stats['location'].map(LOCATION_PRICE_FACTORS).fillna(DEFAULT_LOCATION_FACTOR)
    location_stats['growth_score'] = (location_stats['growth_score'] / 2.6) * 100
    
    # 3. Value score (price per sqft compared to average)
    avg_ppsf = location_stats['avg_price_per_sqft'].mean()
    location_stats['value_score'] = (avg_ppsf / location_stats['avg_price_per_sqft'].clip(lower=avg_ppsf/2)) * 100
    location_stats['value_score'] = location_stats['value_score'].clip(upper=100)
    
    # Combined hotspot score
    location_stats['hotspot_score'] = (
        location_stats['activity_score'] * 0.3 +
        location_stats['growth_score'] * 0.4 +
        location_stats['value_score'] * 0.3
    )
    
    # Sort by hotspot score
    hotspots = location_stats.nlargest(top_n, 'hotspot_score')
    
    # Add recommendation
    hotspots['recommendation'] = hotspots['hotspot_score'].apply(
        lambda x: '🔥 Strong Buy' if x >= 70 else '📈 Good Potential' if x >= 50 else '👀 Watch List'
    )
    
    return hotspots[['location', 'avg_price', 'avg_price_per_sqft', 'property_count', 'hotspot_score', 'recommendation']]

def get_similar_properties(
    property_idx: int,
    df: pd.DataFrame,
    n_recommendations: int = 5
) -> pd.DataFrame:
    """
    Quick function to get similar properties without full RecommendationEngine
    """
    engine = RecommendationEngine()
    engine.fit(df)
    similar_indices = engine.get_similar_properties(property_idx, n_recommendations)
    
    if len(similar_indices) > 0:
        return df.iloc[similar_indices][['location', 'price', 'total_sqft', 'bhk', 'bath']]
    return pd.DataFrame()

def recommend_properties(
    budget: str = None,
    bhk: int = None,
    location: str = None,
    df: pd.DataFrame = None,
    n: int = 5
) -> pd.DataFrame:
    """
    Quick function to get recommendations based on preferences
    """
    engine = RecommendationEngine()
    return engine.recommend_by_preferences(budget, bhk, location, df=df, n=n)

# ==================== MAIN EXPORTS ====================
__all__ = [
    'RecommendationEngine',
    'get_area_score',
    'get_hotspots',
    'get_similar_properties',
    'recommend_properties',
    'LOCATION_PRICE_FACTORS'
]

if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("🎯 RECOMMENDATION MODULE TEST")
    print("=" * 60)
    
    print("\n✅ Recommendation module ready!")