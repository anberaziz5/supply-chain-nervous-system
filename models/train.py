import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def train_predictive_model():
    print("Loading operational data...")
    df = pd.read_csv("data/historical_logistics.csv")
    
    # Feature Engineering
    features = ["Origin_Port", "Destination_Port", "Carrier", "Weather_En_Route", 
                "Container_Weight_Tons", "Port_Congestion_Index", "Route_Distance_NM"]
    X = df[features].copy()
    y = df["Is_Delayed"]
    
    # Encode categorical variables
    encoders = {}
    for col in ["Origin_Port", "Destination_Port", "Carrier", "Weather_En_Route"]:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    print("\nModel Evaluation:")
    print(classification_report(y_test, predictions))
    
    # Save the model and encoders for the backend
    os.makedirs("models/saved", exist_ok=True)
    with open("models/saved/xgboost_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("models/saved/encoders.pkl", "wb") as f:
        pickle.dump(encoders, f)
        
    print("Model and encoders saved to /models/saved/")

if __name__ == "__main__":
    train_predictive_model()