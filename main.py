from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

# 1. Initialize App & Load Brain
app = FastAPI(title="Billing-Guard v2.0")

# Load the model we trained in the previous step
# (Make sure you saved it! If not, run the training script one last time to save 'model.pkl')
# For this example, we assume 'model' is the variable from your training script.
# In production, you would do: model = joblib.load("billing_guard_model.pkl")
# Let's assume you have the model loaded in memory for now or un-comment the line below:
model = joblib.load("billing_guard_model.pkl") 

# 2. Define the Input Format (The Invoice)
class Invoice(BaseModel):
    client_id: int
    cases: int
    images: int
    amount: float

# 3. The "Detective" Function (Explainability)
def explain_flag(cases, images, ratio):
    reasons = []
    
    # Rule 1: The Ratio Trap (The one catching Client 103)
    if ratio > 2.0:
        reasons.append(f"HIGH IMAGE RATIO: {round(ratio, 1)} images per case (Normal is ~0.5)")
        
    # Rule 2: The Volume Trap
    if cases > 1000:
         reasons.append(f"VOLUME SPIKE: {cases} cases is unusually high")
         
    if not reasons:
        return "Unusual statistical pattern detected (General Anomaly)"
        
    return " & ".join(reasons)

# 4. The API Endpoint
@app.post("/verify_invoice")
def verify_invoice(inv: Invoice):
    
    # --- A. Feature Engineering (The same math we used for training) ---
    # Protect against division by zero
    if inv.cases == 0:
        ratio = 0.0
    else:
        ratio = inv.images / inv.cases
        
    # Create the DataFrame for the model
    # MUST match the order of 'features' from your training script: ['img_per_case_ratio', 'cases']
    features = pd.DataFrame([{
        'img_per_case_ratio': ratio,
        'cases': inv.cases
    }])
    
    # --- B. The Prediction ---
    # We use decision_function for the score, predict for the binary flag
    # Note: You need to make sure 'model' is accessible here. 
    # If you are running this in the same script as training, it works.
    # If separate file, load the pickle.
    
    is_anomaly = model.predict(features)[0] == -1
    
    # --- C. The Explanation Layer ---
    if is_anomaly:
        status = "FLAGGED"
        # Call the Detective
        explanation = explain_flag(inv.cases, inv.images, ratio)
    else:
        status = "APPROVED"
        explanation = "Invoice falls within normal behavioral patterns."

    return {
        "status": status,
        "client_id": inv.client_id,
        "risk_factors": {
            "ratio": round(ratio, 2),
            "volume": inv.cases
        },
        "finance_message": explanation
    }

# To run: uvicorn main:app --reload

# if __name__ == "__main__":
    