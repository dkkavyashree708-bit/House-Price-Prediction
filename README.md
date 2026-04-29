# 🏠 House Price Prediction System for Bengaluru - SmartEstate

## 📌 Overview
SmartEstate is a Machine Learning-based web application that predicts house prices in Bengaluru using property features like location, area, and configuration. It helps users estimate fair property values with a simple and interactive interface.

---

## 🎯 Objectives
- Predict house prices based on property features  
- Provide insights for buyers and investors  
- Build a user-friendly prediction system  

---

## 🚀 Key Features
- 🔐 User Authentication (Login / Signup / Guest)
- 🏡 House Price Prediction
- 📍 300+ Bengaluru Locations
- 🗺️ Interactive Maps (Folium)
- 📊 Market Insights Dashboard
- ⚙️ Admin Panel
- 🎨 Modern UI Design  

---

## 🛠️ Tech Stack

**Frontend**
- Streamlit  

**Backend**
- Python  

**Libraries**
- Pandas, NumPy  
- Scikit-learn  
- Plotly, Matplotlib  
- Folium, Geopy  

**Security**
- Hashlib (SHA-256)  

**Data Storage**
- JSON  

---

## ⚙️ System Architecture
- **Frontend**: Streamlit UI  
- **Backend**: Python logic  
- **Model**: Price calculation engine  
- **Database**: JSON file  

---

## 🧠 Algorithm Used
The system uses a rule-based regression approach.

**Input Features**
- Location
- Area (sqft)
- BHK
- Furnishing

**Formula**
Final Price = (5000 × Area) × Location Factor × BHK Factor × Furnishing Factor

**Factors**
- Base Price: ₹5000/sqft  
- Location Factor: 1.0 – 2.5  
- BHK Factor = 1 + (BHK - 2) × 0.1  

**Furnishing Factor**
- Fully: 1.30  
- Semi: 1.15  
- Unfurnished: 1.00  

**Example**
3 BHK, 1500 sqft, Indiranagar (Fully Furnished)  
Final Price ≈ ₹2.67 Crore  

---

## 💻 How to Run
```bash
pip install -r requirements.txt
python app.py
👩‍💻 Author

Kavyashree DK
Final Year IT Student

