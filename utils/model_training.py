import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.model_selection import cross_val_score, GridSearchCV
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Try importing XGBoost and LightGBM if available
try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("⚠️ XGBoost not available. Install with: pip install xgboost")

try:
    from lightgbm import LGBMRegressor
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False
    print("⚠️ LightGBM not available. Install with: pip install lightgbm")

from .data_preprocessing import load_and_preprocess_data

# ==================== MODEL CONFIGURATION ====================
RANDOM_STATE = 42
CV_FOLDS = 5
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Hyperparameter grids for tuning
PARAM_GRIDS = {
    'Random Forest': {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 15, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    },
    'Gradient Boosting': {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 7]
    },
    'XGBoost': {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 1.0]
    },
    'Ridge': {
        'alpha': [0.1, 1.0, 10.0, 100.0]
    },
    'Lasso': {
        'alpha': [0.001, 0.01, 0.1, 1.0]
    }
}

def get_models():
    """Get dictionary of regression models"""
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(random_state=RANDOM_STATE),
        'Lasso Regression': Lasso(random_state=RANDOM_STATE),
        'Elastic Net': ElasticNet(random_state=RANDOM_STATE),
        'Decision Tree': DecisionTreeRegressor(random_state=RANDOM_STATE),
        'Random Forest': RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(random_state=RANDOM_STATE),
        'AdaBoost': AdaBoostRegressor(random_state=RANDOM_STATE),
        'KNN': KNeighborsRegressor(n_jobs=-1),
        'SVR': SVR()
    }
    
    # Add XGBoost if available
    if XGB_AVAILABLE:
        models['XGBoost'] = XGBRegressor(random_state=RANDOM_STATE, n_jobs=-1)
    
    # Add LightGBM if available
    if LGBM_AVAILABLE:
        models['LightGBM'] = LGBMRegressor(random_state=RANDOM_STATE, n_jobs=-1)
    
    return models

def train_models_with_cv(X_train, y_train, models):
    """Train models with cross-validation"""
    results = []
    
    for name, model in models.items():
        try:
            # Perform cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring='r2')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Train on full training set
            model.fit(X_train, y_train)
            
            results.append({
                'Model': name,
                'CV Mean R2': round(cv_mean, 4),
                'CV Std': round(cv_std, 4),
                'Status': 'Trained'
            })
            
            print(f"   {name}: CV R2 = {cv_mean:.4f} (±{cv_std:.4f})")
            
        except Exception as e:
            print(f"   {name}: Error - {str(e)[:50]}")
            results.append({
                'Model': name,
                'CV Mean R2': None,
                'CV Std': None,
                'Status': f'Error: {str(e)[:30]}'
            })
    
    return pd.DataFrame(results)

def tune_hyperparameters(X_train, y_train, model_name, param_grid):
    """Perform hyperparameter tuning using GridSearchCV"""
    print(f"\n🔧 Tuning hyperparameters for {model_name}...")
    
    if model_name == 'Random Forest':
        model = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1)
    elif model_name == 'Gradient Boosting':
        model = GradientBoostingRegressor(random_state=RANDOM_STATE)
    elif model_name == 'XGBoost' and XGB_AVAILABLE:
        model = XGBRegressor(random_state=RANDOM_STATE, n_jobs=-1)
    elif model_name == 'Ridge':
        model = Ridge(random_state=RANDOM_STATE)
    elif model_name == 'Lasso':
        model = Lasso(random_state=RANDOM_STATE)
    else:
        return None, None
    
    try:
        grid_search = GridSearchCV(
            model, param_grid, cv=CV_FOLDS, 
            scoring='r2', n_jobs=-1, verbose=0
        )
        grid_search.fit(X_train, y_train)
        
        print(f"   Best parameters: {grid_search.best_params_}")
        print(f"   Best CV score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_, grid_search.best_params_
    except Exception as e:
        print(f"   Tuning failed: {e}")
        return None, None

def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model performance on test set"""
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = mean_absolute_percentage_error(y_test, y_pred) * 100
    
    # Calculate additional metrics
    explained_variance = 1 - (np.var(y_test - y_pred) / np.var(y_test))
    
    # Calculate accuracy within thresholds
    accuracy_10 = np.mean(np.abs((y_pred - y_test) / y_test) <= 0.10) * 100
    accuracy_15 = np.mean(np.abs((y_pred - y_test) / y_test) <= 0.15) * 100
    accuracy_20 = np.mean(np.abs((y_pred - y_test) / y_test) <= 0.20) * 100
    
    metrics = {
        'Model': model_name,
        'R2 Score': round(r2, 4),
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2),
        'MAPE (%)': round(mape, 2),
        'Explained Variance': round(explained_variance, 4),
        'Accuracy (±10%)': round(accuracy_10, 2),
        'Accuracy (±15%)': round(accuracy_15, 2),
        'Accuracy (±20%)': round(accuracy_20, 2)
    }
    
    return metrics, y_pred

def plot_predictions(y_test, y_pred, model_name):
    """Plot actual vs predicted values"""
    plt.figure(figsize=(12, 4))
    
    # Scatter plot
    plt.subplot(1, 2, 1)
    plt.scatter(y_test, y_pred, alpha=0.5, color='#8B5CF6')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, color='#F97316')
    plt.xlabel('Actual Price (Lakhs)')
    plt.ylabel('Predicted Price (Lakhs)')
    plt.title(f'{model_name}: Actual vs Predicted')
    
    # Residual plot
    plt.subplot(1, 2, 2)
    residuals = y_test - y_pred
    plt.scatter(y_pred, residuals, alpha=0.5, color='#8B5CF6')
    plt.axhline(y=0, color='r', linestyle='--', linewidth=2)
    plt.xlabel('Predicted Price (Lakhs)')
    plt.ylabel('Residuals')
    plt.title(f'{model_name}: Residual Plot')
    
    plt.tight_layout()
    return plt.gcf()

def save_models(models_dict, best_model, best_model_name, metrics_df, feature_cols):
    """Save all trained models and artifacts"""
    os.makedirs('models', exist_ok=True)
    
    # Save all models
    joblib.dump(models_dict, 'models/all_models.pkl')
    print("✅ All models saved to models/all_models.pkl")
    
    # Save best model
    joblib.dump(best_model, 'models/best_model.pkl')
    print(f"✅ Best model ({best_model_name}) saved to models/best_model.pkl")
    
    # Save metrics
    metrics_df.to_csv('models/model_metrics.csv', index=False)
    print("✅ Model metrics saved to models/model_metrics.csv")
    
    # Save feature columns
    joblib.dump(feature_cols, 'models/feature_columns.pkl')
    print("✅ Feature columns saved to models/feature_columns.pkl")

def load_trained_models():
    """Load all trained models"""
    try:
        models = joblib.load('models/all_models.pkl')
        best_model = joblib.load('models/best_model.pkl')
        metrics = pd.read_csv('models/model_metrics.csv')
        feature_cols = joblib.load('models/feature_columns.pkl')
        
        print("✅ Models loaded successfully")
        return models, best_model, metrics, feature_cols
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return None, None, None, None

def get_best_model():
    """Get the best trained model"""
    try:
        best_model = joblib.load('models/best_model.pkl')
        return best_model
    except:
        return None

def train_models(perform_tuning=True):
    """Main function to train all models"""
    
    print("=" * 70)
    print("🤖 MODEL TRAINING PIPELINE")
    print("=" * 70)
    
    try:
        # Load preprocessed data
        X_train, X_val, X_test, y_train, y_val, y_test, df, feature_cols = load_and_preprocess_data()
        
        print(f"\n📊 Data shapes:")
        print(f"   Training: {X_train.shape}")
        print(f"   Validation: {X_val.shape}")
        print(f"   Test: {X_test.shape}")
        print(f"   Features: {len(feature_cols)}")
        
        # Get models
        models = get_models()
        print(f"\n📋 Models to train: {len(models)}")
        
        # Train with cross-validation
        print("\n" + "=" * 50)
        print("📊 CROSS-VALIDATION RESULTS")
        print("=" * 50)
        cv_results = train_models_with_cv(X_train, y_train, models)
        
        # Evaluate on test set
        print("\n" + "=" * 50)
        print("📊 TEST SET EVALUATION")
        print("=" * 50)
        
        all_metrics = []
        best_score = -float('inf')
        best_model = None
        best_model_name = None
        best_predictions = None
        
        for name, model in models.items():
            # Check if model was trained successfully
            if name in cv_results['Model'].values:
                try:
                    metrics, y_pred = evaluate_model(model, X_test, y_test, name)
                    all_metrics.append(metrics)
                    
                    print(f"\n   {name}:")
                    print(f"      R² Score: {metrics['R2 Score']:.4f}")
                    print(f"      MAE: ₹{metrics['MAE']:.2f} Lakhs")
                    print(f"      RMSE: ₹{metrics['RMSE']:.2f} Lakhs")
                    print(f"      MAPE: {metrics['MAPE (%)']:.2f}%")
                    print(f"      Accuracy (±15%): {metrics['Accuracy (±15%)']:.1f}%")
                    
                    # Track best model
                    if metrics['R2 Score'] > best_score:
                        best_score = metrics['R2 Score']
                        best_model = model
                        best_model_name = name
                        best_predictions = y_pred
                        
                except Exception as e:
                    print(f"\n   {name}: Evaluation failed - {e}")
        
        # Hyperparameter tuning for best model
        if perform_tuning and best_model_name in PARAM_GRIDS:
            print("\n" + "=" * 50)
            print("🔧 HYPERPARAMETER TUNING")
            print("=" * 50)
            
            tuned_model, best_params = tune_hyperparameters(
                X_train, y_train, best_model_name, PARAM_GRIDS[best_model_name]
            )
            
            if tuned_model:
                # Evaluate tuned model
                metrics_tuned, y_pred_tuned = evaluate_model(tuned_model, X_test, y_test, f"{best_model_name} (Tuned)")
                print(f"\n   Tuned {best_model_name}:")
                print(f"      R² Score: {metrics_tuned['R2 Score']:.4f}")
                print(f"      MAE: ₹{metrics_tuned['MAE']:.2f} Lakhs")
                
                if metrics_tuned['R2 Score'] > best_score:
                    best_model = tuned_model
                    best_model_name = f"{best_model_name} (Tuned)"
                    best_score = metrics_tuned['R2 Score']
                    best_predictions = y_pred_tuned
                    all_metrics.append(metrics_tuned)
        
        # Create metrics dataframe
        metrics_df = pd.DataFrame(all_metrics)
        metrics_df = metrics_df.sort_values('R2 Score', ascending=False)
        
        print("\n" + "=" * 50)
        print("🏆 MODEL RANKING")
        print("=" * 50)
        print(metrics_df[['Model', 'R2 Score', 'MAE', 'MAPE (%)']].to_string(index=False))
        
        # Generate plots for best model
        try:
            fig = plot_predictions(y_test, best_predictions, best_model_name)
            fig.savefig('models/best_model_predictions.png', dpi=100, bbox_inches='tight')
            plt.close()
            print("\n✅ Prediction plot saved to models/best_model_predictions.png")
        except Exception as e:
            print(f"⚠️ Could not save prediction plot: {e}")
        
        # Generate feature importance plot for tree-based models
        if hasattr(best_model, 'feature_importances_'):
            try:
                importances = best_model.feature_importances_
                if len(importances) == len(feature_cols):
                    feature_importance_df = pd.DataFrame({
                        'feature': feature_cols,
                        'importance': importances
                    }).sort_values('importance', ascending=False)
                    
                    plt.figure(figsize=(10, 6))
                    sns.barplot(data=feature_importance_df.head(10), x='importance', y='feature', palette='Purples')
                    plt.title(f'Top 10 Feature Importances - {best_model_name}')
                    plt.xlabel('Importance')
                    plt.tight_layout()
                    plt.savefig('models/feature_importance.png', dpi=100, bbox_inches='tight')
                    plt.close()
                    print("✅ Feature importance plot saved to models/feature_importance.png")
            except Exception as e:
                print(f"⚠️ Could not save feature importance: {e}")
        
        # Save all models
        save_models(models, best_model, best_model_name, metrics_df, feature_cols)
        
        print("\n" + "=" * 70)
        print(f"✅ TRAINING COMPLETE!")
        print(f"   Best Model: {best_model_name}")
        print(f"   R² Score: {best_score:.4f}")
        print("=" * 70)
        
        return best_model, metrics_df
        
    except Exception as e:
        print(f"\n❌ Error in training pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def quick_train():
    """Quick training without hyperparameter tuning"""
    return train_models(perform_tuning=False)

if __name__ == "__main__":
    # Run full training pipeline
    best_model, metrics = train_models()
    
    if best_model:
        print("\n🎉 Model training completed successfully!")
        print("   Models saved in 'models/' directory")
    else:
        print("\n❌ Model training failed. Please check your data.")
def save_model(model, filepath='models/best_model.pkl'):
    """Save a single model to file"""
    import joblib
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"✅ Model saved to {filepath}")