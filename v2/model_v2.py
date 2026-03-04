import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import os

# Path to the dataset
dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gym_footfall_dataset.csv')

def load_and_preprocess_data(filepath):
    df = pd.read_csv(filepath)
    
    # Identify categorical columns
    categorical_cols = ['exam_phase', 'weather_condition', 'maintenance_severity']
    
    # Encode categorical columns
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
        
    # Drop columns that are not useful for prediction or represent target leakage
    # raw_demand and base_demand are highly correlated to the target so we shouldn't use them as features.
    X = df.drop(columns=['date', 'daily_gym_footfall', 'raw_demand', 'base_demand'])
    y = df['daily_gym_footfall']
    
    return X, y, label_encoders

def train_and_evaluate():
    print(f"Loading dataset from: {dataset_path}")
    X, y, label_encoders = load_and_preprocess_data(dataset_path)
    
    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Keep track of testing 'is_gym_open' to enforce our condition
    is_gym_open_test = X_test['is_gym_open'].values
    
    # Train the Random Forest model
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    print("Making predictions...")
    y_pred = model.predict(X_test)
    
    # --- IMPORTANT CONDITION ---
    # If gym is closed, footfall MUST be 0
    print("Applying condition: if gym is closed, footfall is 0")
    y_pred = np.where(is_gym_open_test == 0, 0, y_pred)
    
    # Footfall should be a whole number
    y_pred = np.round(y_pred)
    
    # Evaluate
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print("\n--- Model Evaluation ---")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
    
    return model, label_encoders

# Helper function to showcase how to predict on new data
def predict_footfall(model, input_df):
    """
    Predict footfall incorporating the 'gym closed = 0 footfall' condition.
    """
    pred = model.predict(input_df)
    
    # Ensure it's 0 when closed
    closed_mask = input_df['is_gym_open'] == 0
    pred[closed_mask] = 0
    
    return np.round(pred)

if __name__ == "__main__":
    trained_model, encoders = train_and_evaluate()

#Pkl the model
import joblib
joblib.dump(trained_model, 'gym_footfall_model_v2.pkl')
print("saved as gym_footfall_model_v2.pkl")