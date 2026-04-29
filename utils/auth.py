# utils/auth.py
import streamlit as st
import hashlib
import json
import os
from datetime import datetime

# ==================== THEME STYLES FOR AUTH PAGES ====================
def apply_auth_theme():
    """Apply theme styling for authentication pages"""
    st.markdown("""
    <style>
        /* Glassmorphism Effect */
        .auth-container {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
            transition: all 0.3s ease;
        }
        
        .auth-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
            border-color: rgba(249, 115, 22, 0.3);
        }
        
        /* Headers */
        .auth-title {
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .auth-subtitle {
            text-align: center;
            color: #1F2937;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #8B5CF6, #F97316);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            border-radius: 12px !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #F97316 !important;
            box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2) !important;
        }
        
        /* Checkbox */
        .stCheckbox > label {
            color: #1F2937 !important;
        }
        
        /* Divider */
        .auth-divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 20px 0;
            color: #8B5CF6;
        }
        
        .auth-divider::before,
        .auth-divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid rgba(139, 92, 246, 0.3);
        }
        
        .auth-divider::before {
            margin-right: 15px;
        }
        
        .auth-divider::after {
            margin-left: 15px;
        }
        
        /* Info/Warning/Success */
        .stAlert {
            border-radius: 12px;
            border-left: 4px solid #F97316;
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== USER DATABASE FUNCTIONS ====================
USER_DB_FILE = "users.json"

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return create_default_users()
    return create_default_users()

def create_default_users():
    """Create default admin user"""
    default_users = {
        "admin@smartestate.com": {
            "password": hash_password("admin123"),
            "user_type": "admin",
            "created_at": str(datetime.now()),
            "name": "Super Admin",
            "last_login": None
        }
    }
    save_users(default_users)
    return default_users

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USER_DB_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return True
    except:
        return False

def create_user(email, password, name="User"):
    """
    Create a new user account
    Returns (success, message)
    """
    users = load_users()
    
    if not email or not password:
        return False, "Email and password are required!"
    
    if email in users:
        return False, "Email already exists! Please use a different email."
    
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address!"
    
    if len(password) < 4:
        return False, "Password must be at least 4 characters long!"
    
    users[email] = {
        "password": hash_password(password),
        "user_type": "user",
        "created_at": str(datetime.now()),
        "name": name if name else email.split('@')[0],
        "last_login": None
    }
    
    if save_users(users):
        return True, f"Account created successfully! Welcome {name}!"
    else:
        return False, "Error saving user data. Please try again."

def verify_user(email, password):
    """
    Verify user credentials
    Returns (success, user_type)
    """
    users = load_users()
    
    if not email or not password:
        return False, None
    
    if email in users and users[email]["password"] == hash_password(password):
        # Update last login time
        users[email]["last_login"] = str(datetime.now())
        save_users(users)
        return True, users[email]["user_type"]
    
    return False, None

def login(email, password):
    """
    Simple authentication function
    Returns (success, user_type)
    """
    # Admin login (hardcoded for security)
    if email == "admin@smartestate.com" and password == "admin123":
        return True, "admin"
    
    # Check against user database
    success, user_type = verify_user(email, password)
    if success:
        return True, user_type
    
    # Demo mode - any email/password works for regular users
    if email and password and "@" in email:
        # Auto-create demo user if doesn't exist
        users = load_users()
        if email not in users:
            create_user(email, password, email.split('@')[0])
        return True, "user"
    
    return False, None

def logout():
    """Clear session state and logout"""
    try:
        import streamlit as st
        # Clear all session state keys
        keys_to_clear = ['authenticated', 'page', 'user_type', 'user_email', 'show_signup', 
                        'current_page', 'prediction_result', 'selected_location', 'advanced_options']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Clear any remaining keys
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        return True
    except Exception as e:
        print(f"Logout error: {e}")
        return False

def is_admin():
    """Check if current user is admin"""
    import streamlit as st
    return st.session_state.get('user_type') == 'admin'

def is_authenticated():
    """Check if user is authenticated"""
    import streamlit as st
    return st.session_state.get('authenticated', False)

def get_current_user():
    """Get current user email"""
    import streamlit as st
    return st.session_state.get('user_email', None)

def get_user_name():
    """Get current user name"""
    import streamlit as st
    email = st.session_state.get('user_email', None)
    if email:
        users = load_users()
        if email in users:
            return users[email].get('name', email.split('@')[0])
    return "Guest"

def update_user_profile(email, name=None, password=None):
    """
    Update user profile information
    Returns (success, message)
    """
    users = load_users()
    
    if email not in users:
        return False, "User not found!"
    
    if name:
        users[email]["name"] = name
    
    if password:
        if len(password) < 4:
            return False, "Password must be at least 4 characters!"
        users[email]["password"] = hash_password(password)
    
    if save_users(users):
        return True, "Profile updated successfully!"
    return False, "Error updating profile!"

def delete_user_account(email):
    """
    Delete user account (cannot delete main admin)
    Returns (success, message)
    """
    if email == "admin@smartestate.com":
        return False, "Cannot delete the main admin account!"
    
    users = load_users()
    if email in users:
        del users[email]
        if save_users(users):
            return True, "Account deleted successfully!"
    
    return False, "Error deleting account!"

def get_all_users():
    """Get all registered users (admin only)"""
    users = load_users()
    user_list = []
    for email, data in users.items():
        user_list.append({
            'email': email,
            'name': data.get('name', email.split('@')[0]),
            'user_type': data.get('user_type', 'user'),
            'created_at': data.get('created_at', 'N/A'),
            'last_login': data.get('last_login', 'Never')
        })
    return user_list

def get_user_stats():
    """Get user statistics (admin only)"""
    users = load_users()
    total = len(users)
    admin_count = sum(1 for u in users.values() if u.get('user_type') == 'admin')
    user_count = total - admin_count
    
    return {
        'total_users': total,
        'admin_users': admin_count,
        'regular_users': user_count,
        'recent_users': len([u for u in users.values() if u.get('created_at', '').startswith(str(datetime.now().date()))])
    }