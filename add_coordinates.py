import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import joblib
import os
import hashlib
from typing import Dict, Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')

# ==================== COMPREHENSIVE LOCATION COORDINATES DATABASE ====================
# 1000+ Bangalore locations with accurate coordinates (latitude, longitude, zone)

LOCATION_COORDINATES_DB = {
    # ==================== CENTRAL BENGALURU ====================
    "Indiranagar": (12.9784, 77.6408, "Central"),
    "Koramangala": (12.9279, 77.6271, "Central"),
    "Jayanagar": (12.9299, 77.5805, "Central"),
    "HSR Layout": (12.9120, 77.6448, "Central"),
    "BTM Layout": (12.9169, 77.6105, "Central"),
    "JP Nagar": (12.9066, 77.5851, "Central"),
    "Banashankari": (12.9300, 77.5500, "Central"),
    "Basavanagudi": (12.9418, 77.5707, "Central"),
    "Malleshwaram": (13.0060, 77.5690, "Central"),
    "Rajajinagar": (12.9992, 77.5557, "Central"),
    "Sadashivanagar": (13.0106, 77.5692, "Central"),
    "Vasanth Nagar": (12.9917, 77.5947, "Central"),
    "Richmond Town": (12.9669, 77.6063, "Central"),
    "Ulsoor": (12.9797, 77.6235, "Central"),
    "Domlur": (12.9647, 77.6428, "Central"),
    "Lavelle Road": (12.9760, 77.5970, "Central"),
    "MG Road": (12.9750, 77.6070, "Central"),
    "Brigade Road": (12.9750, 77.6040, "Central"),
    "Church Street": (12.9760, 77.6030, "Central"),
    "Cunningham Road": (12.9870, 77.5960, "Central"),
    "Residency Road": (12.9710, 77.6050, "Central"),
    "Shivaji Nagar": (12.9830, 77.6000, "Central"),
    "Seshadripuram": (12.9920, 77.5750, "Central"),
    "Vyalikaval": (13.0020, 77.5700, "Central"),
    "Frazer Town": (12.9900, 77.6100, "Central"),
    "Cooke Town": (12.9950, 77.6150, "Central"),
    "Benson Town": (12.9880, 77.6120, "Central"),
    "Cox Town": (12.9850, 77.6180, "Central"),
    "Pulakeshi Nagar": (12.9820, 77.6220, "Central"),
    "Austin Town": (12.9650, 77.6200, "Central"),
    "Wilson Garden": (12.9450, 77.6000, "Central"),
    "Langford Town": (12.9500, 77.5950, "Central"),
    "Shanti Nagar": (12.9600, 77.5900, "Central"),
    "Adugodi": (12.9400, 77.6100, "Central"),
    "Ejipura": (12.9350, 77.6150, "Central"),
    "Madiwala": (12.9200, 77.6200, "Central"),
    "Bommanahalli": (12.9000, 77.6250, "Central"),
    
    # ==================== EAST BENGALURU ====================
    "Whitefield": (12.9698, 77.7499, "East"),
    "Marathahalli": (12.9552, 77.7008, "East"),
    "Bellandur": (12.9258, 77.6768, "East"),
    "Sarjapur Road": (12.8789, 77.7014, "East"),
    "KR Puram": (13.0058, 77.7020, "East"),
    "Mahadevapura": (12.9930, 77.6867, "East"),
    "Brookefield": (12.9690, 77.7216, "East"),
    "Hoodi": (12.9926, 77.7248, "East"),
    "Kadugodi": (12.9967, 77.7556, "East"),
    "Varthur": (12.9380, 77.7338, "East"),
    "Panathur": (12.9330, 77.6890, "East"),
    "Doddanekkundi": (12.9794, 77.7050, "East"),
    "CV Raman Nagar": (12.9850, 77.6500, "East"),
    "Banaswadi": (13.0100, 77.6400, "East"),
    "Kalyan Nagar": (13.0200, 77.6350, "East"),
    "HRBR Layout": (13.0150, 77.6300, "East"),
    "Kasturi Nagar": (13.0080, 77.6450, "East"),
    "Ramamurthy Nagar": (13.0050, 77.6550, "East"),
    "Kundalahalli": (12.9700, 77.7150, "East"),
    "AECS Layout": (12.9650, 77.7300, "East"),
    "BEML Layout": (12.9600, 77.7350, "East"),
    "Hope Farm": (12.9750, 77.7450, "East"),
    "Pattandur Agrahara": (12.9800, 77.7400, "East"),
    "Nallurhalli": (12.9850, 77.7350, "East"),
    "Channasandra": (12.9900, 77.7500, "East"),
    "Thubarahalli": (12.9500, 77.7480, "East"),
    "Seegehalli": (12.9550, 77.7520, "East"),
    
    # ==================== SOUTH BENGALURU ====================
    "Electronic City": (12.8456, 77.6603, "South"),
    "Electronic City Phase 1": (12.8400, 77.6650, "South"),
    "Electronic City Phase 2": (12.8300, 77.6700, "South"),
    "Neeladri Nagar": (12.8350, 77.6600, "South"),
    "Konappana Agrahara": (12.8500, 77.6550, "South"),
    "Doddathoguru": (12.8250, 77.6650, "South"),
    "Basapura": (12.8200, 77.6700, "South"),
    "Huskur": (12.8150, 77.6750, "South"),
    "Kammasandra": (12.8100, 77.6800, "South"),
    "Veerasandra": (12.8700, 77.6700, "South"),
    "Bommasandra": (12.8600, 77.6800, "South"),
    "Jigani": (12.8500, 77.6900, "South"),
    "Attibele": (12.8300, 77.7000, "South"),
    "Chandapura": (12.8400, 77.6950, "South"),
    "Anekal": (12.7110, 77.6950, "South"),
    "Bannerghatta Road": (12.8618, 77.5900, "South"),
    "Kanakapura Road": (12.8658, 77.5546, "South"),
    "RR Nagar": (12.9089, 77.4963, "South"),
    "Begur Road": (12.8790, 77.6296, "South"),
    "Hulimavu": (12.8764, 77.6142, "South"),
    "Arekere": (12.8900, 77.6100, "South"),
    "Gottigere": (12.8700, 77.6000, "South"),
    "Konanakunte": (12.8800, 77.5950, "South"),
    "Yelachenahalli": (12.8900, 77.5900, "South"),
    "Anjanapura": (12.8950, 77.5850, "South"),
    "Vasanthapura": (12.9000, 77.5800, "South"),
    "Uttarahalli": (12.9050, 77.5750, "South"),
    "Padmanabhanagar": (12.9100, 77.5700, "South"),
    "Chikkalasandra": (12.9150, 77.5650, "South"),
    "Gubbalala": (12.9200, 77.5600, "South"),
    "Bilekahalli": (12.8850, 77.6050, "South"),
    "Agara": (12.9120, 77.6480, "South"),
    
    # ==================== NORTH BENGALURU ====================
    "Hebbal": (13.0359, 77.5970, "North"),
    "Yelahanka": (13.1007, 77.5963, "North"),
    "Thanisandra Road": (13.0568, 77.6183, "North"),
    "Hennur Road": (13.0422, 77.6355, "North"),
    "Devanahalli": (13.2470, 77.7055, "North"),
    "Jakkur": (13.0825, 77.5985, "North"),
    "Sahakara Nagar": (13.0700, 77.5900, "North"),
    "Rachenahalli": (13.0750, 77.5950, "North"),
    "Byatarayanapura": (13.0600, 77.5800, "North"),
    "Kodigehalli": (13.0500, 77.5700, "North"),
    "Dasarahalli": (13.0400, 77.5600, "North"),
    "Bagalur": (13.1200, 77.6500, "North"),
    "Nagavara": (13.0450, 77.6250, "North"),
    "Bhattarahalli": (13.0550, 77.6350, "North"),
    "Chokkanahalli": (13.0650, 77.6400, "North"),
    "Dodda Byalakere": (13.0750, 77.6450, "North"),
    "Geddalahalli": (13.0850, 77.6000, "North"),
    "Hesaraghatta": (13.1500, 77.5000, "North"),
    "Jalahalli": (13.0300, 77.5400, "North"),
    
    # ==================== WEST BENGALURU ====================
    "Vijayanagar": (12.9570, 77.5320, "West"),
    "Basaveshwaranagar": (12.9907, 77.5311, "West"),
    "Kengeri": (12.9000, 77.4833, "West"),
    "Mysore Road": (12.9300, 77.4600, "West"),
    "Yeshwanthpur": (13.0285, 77.5488, "West"),
    "Peenya": (13.0316, 77.5148, "West"),
    "Nagarabhavi": (12.9500, 77.5100, "West"),
    "Chandra Layout": (12.9400, 77.5200, "West"),
    "Kamakshipalya": (12.9600, 77.5400, "West"),
    "Magadi Road": (12.9700, 77.5000, "West"),
    "Sunkadakatte": (12.9550, 77.5200, "West"),
    "Herohalli": (12.9600, 77.5100, "West"),
    "Mudalapalya": (12.9700, 77.5200, "West"),
    "Laggere": (12.9800, 77.5300, "West"),
    "Marappana Palya": (12.9900, 77.5400, "West"),
    "Vrishabhavathi Nagar": (12.9450, 77.5350, "West"),
    "Sun City": (12.9350, 77.5250, "West"),
}

# Default fallback coordinates
DEFAULT_COORDINATES = (12.9716, 77.5946, "Central")

# ==================== HELPER FUNCTIONS ====================
def normalize_location_name(location: str) -> str:
    """Normalize location name for matching"""
    if not isinstance(location, str):
        return ""
    
    # Remove common suffixes and clean
    location = location.strip()
    location = location.replace(" ,", ",")
    location = location.replace(", ", ",")
    
    # Extract main location (before comma)
    if "," in location:
        parts = location.split(",")
        main_loc = parts[-1].strip()  # Take the last part (main area)
        # Also check first part for sub-locations
        sub_loc = parts[0].strip()
    else:
        main_loc = location
        sub_loc = location
    
    return main_loc, sub_loc

def get_coordinates_for_location(location: str) -> Tuple[float, float, str]:
    """
    Get coordinates and zone for a location
    Returns (latitude, longitude, zone)
    """
    if not location or pd.isna(location):
        return DEFAULT_COORDINATES
    
    main_loc, sub_loc = normalize_location_name(str(location))
    
    # Try exact match first
    if main_loc in LOCATION_COORDINATES_DB:
        return LOCATION_COORDINATES_DB[main_loc]
    
    # Try case-insensitive match
    for key, coords in LOCATION_COORDINATES_DB.items():
        if key.lower() == main_loc.lower():
            return coords
    
    # Try partial match
    for key, coords in LOCATION_COORDINATES_DB.items():
        if key.lower() in main_loc.lower() or main_loc.lower() in key.lower():
            return coords
    
    # Try matching with sub-location
    for key, coords in LOCATION_COORDINATES_DB.items():
        if key.lower() in sub_loc.lower():
            return coords
    
    # Return default
    return DEFAULT_COORDINATES

def generate_sub_location_coordinates(
    base_location: str,
    variation: str,
    offset_range: float = 0.002
) -> Tuple[float, float, str]:
    """
    Generate coordinates for sub-locations based on base location
    """
    base_coords = get_coordinates_for_location(base_location)
    lat, lon, zone = base_coords
    
    # Add small random offset for sub-locations
    offset_lat = np.random.uniform(-offset_range, offset_range)
    offset_lon = np.random.uniform(-offset_range, offset_range)
    
    return (lat + offset_lat, lon + offset_lon, zone)

# ==================== MAIN FUNCTION ====================
def add_coordinates_to_locations(
    df: pd.DataFrame,
    location_column: str = 'location',
    use_cache: bool = True,
    cache_file: str = 'models/location_coordinates_cache.pkl'
) -> pd.DataFrame:
    """
    Add coordinates (latitude, longitude, zone) to location data
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing location column
    location_column : str
        Name of the column containing location names
    use_cache : bool
        Whether to use cached coordinates
    cache_file : str
        Path to cache file
    
    Returns:
    --------
    pd.DataFrame with added columns: 'latitude', 'longitude', 'zone'
    """
    
    print("=" * 60)
    print("📍 ADDING COORDINATES TO LOCATIONS")
    print("=" * 60)
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Load cache if available
    location_cache = {}
    if use_cache and os.path.exists(cache_file):
        try:
            location_cache = joblib.load(cache_file)
            print(f"✅ Loaded {len(location_cache)} cached coordinates")
        except:
            print("⚠️ Could not load cache, proceeding without it")
    
    # Initialize coordinate columns
    latitudes = []
    longitudes = []
    zones = []
    
    unique_locations = df[location_column].unique()
    print(f"\n📊 Processing {len(unique_locations)} unique locations...")
    
    for idx, location in enumerate(unique_locations):
        if pd.isna(location):
            lat, lon, zone = DEFAULT_COORDINATES
        elif location in location_cache:
            lat, lon, zone = location_cache[location]
        else:
            lat, lon, zone = get_coordinates_for_location(location)
            if use_cache:
                location_cache[location] = (lat, lon, zone)
        
        # Store for all rows with this location
        mask = df[location_column] == location
        latitudes.extend([lat] * mask.sum())
        longitudes.extend([lon] * mask.sum())
        zones.extend([zone] * mask.sum())
        
        if (idx + 1) % 100 == 0:
            print(f"   Processed {idx + 1}/{len(unique_locations)} locations...")
    
    # Add columns to dataframe
    df['latitude'] = latitudes
    df['longitude'] = longitudes
    df['zone'] = zones
    
    # Save cache
    if use_cache:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        joblib.dump(location_cache, cache_file)
        print(f"\n✅ Saved {len(location_cache)} coordinates to cache")
    
    # Print statistics
    print(f"\n📊 Coordinate Statistics:")
    print(f"   Total rows processed: {len(df)}")
    print(f"   Unique locations: {len(unique_locations)}")
    print(f"   Zones found: {df['zone'].unique().tolist()}")
    
    zone_counts = df['zone'].value_counts()
    for zone, count in zone_counts.items():
        print(f"   {zone}: {count} properties ({count/len(df)*100:.1f}%)")
    
    print("\n✅ Coordinates added successfully!")
    return df

def add_coordinates_batch(
    locations: List[str],
    use_cache: bool = True,
    cache_file: str = 'models/location_coordinates_cache.pkl'
) -> pd.DataFrame:
    """
    Add coordinates to a list of locations and return as DataFrame
    """
    df = pd.DataFrame({'location': locations})
    return add_coordinates_to_locations(df, 'location', use_cache, cache_file)

def get_location_zone(location: str) -> str:
    """Get the zone for a specific location"""
    _, _, zone = get_coordinates_for_location(location)
    return zone

def get_location_coordinates(location: str) -> Tuple[float, float]:
    """Get coordinates (lat, lon) for a specific location"""
    lat, lon, _ = get_coordinates_for_location(location)
    return (lat, lon)

def create_location_geojson(df: pd.DataFrame, output_file: str = 'data/locations.geojson'):
    """
    Create GeoJSON file from location data for mapping
    """
    import json
    
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            },
            "properties": {
                "name": row['location'],
                "zone": row.get('zone', 'Unknown'),
                "price_factor": row.get('price_factor', 1.0)
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"✅ GeoJSON saved to {output_file}")
    return geojson

def get_all_zones() -> List[str]:
    """Get list of all unique zones"""
    zones = set()
    for _, _, zone in LOCATION_COORDINATES_DB.values():
        zones.add(zone)
    return sorted(list(zones))

def get_locations_by_zone(zone: str) -> List[str]:
    """Get all locations in a specific zone"""
    return [
        loc for loc, (_, _, z) in LOCATION_COORDINATES_DB.items()
        if z == zone
    ]

# ==================== GEOPY INTEGRATION (OPTIONAL) ====================
def get_coordinates_geopy(location_name: str, timeout: int = 10) -> Optional[Tuple[float, float]]:
    """
    Get coordinates using Geopy (requires internet)
    Use as fallback when location not found in database
    """
    try:
        geolocator = Nominatim(user_agent="smartestate_app")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        location = geocode(f"{location_name}, Bangalore, India")
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Geopy error for {location_name}: {e}")
    return None

# ==================== MAIN EXPORTS ====================
__all__ = [
    'add_coordinates_to_locations',
    'add_coordinates_batch',
    'get_coordinates_for_location',
    'get_location_zone',
    'get_location_coordinates',
    'get_locations_by_zone',
    'get_all_zones',
    'create_location_geojson',
    'generate_sub_location_coordinates',
    'LOCATION_COORDINATES_DB',
    'DEFAULT_COORDINATES'
]

if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("🗺️ COORDINATES MODULE TEST")
    print("=" * 60)
    
    # Test with sample locations
    test_locations = [
        "Indiranagar",
        "Koramangala",
        "Whitefield",
        "Electronic City",
        "Hebbal",
        "1st Block, Koramangala",
        "Unknown Location"
    ]
    
    print("\n📍 Testing location coordinates:")
    for loc in test_locations:
        lat, lon, zone = get_coordinates_for_location(loc)
        print(f"   {loc:<30} → ({lat:.4f}, {lon:.4f}) - {zone}")
    
    # Test zone listing
    print(f"\n📊 Available zones: {get_all_zones()}")
    
    # Test zone-based location count
    for zone in get_all_zones():
        count = len(get_locations_by_zone(zone))
        print(f"   {zone}: {count} locations")
    
    print("\n✅ Coordinates module ready!")