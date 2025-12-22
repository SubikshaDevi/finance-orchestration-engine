import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# 1. Load the Data
df = pd.read_csv("invoices_v2.csv")

# 2. FEATURE ENGINEERING (The Secret Sauce)
# We don't just look at '$'. We look at the RELATIONSHIP between items.
# Avoid division by zero by using a small epsilon if cases is 0 (though our data is safe)
df['img_per_case_ratio'] = df['images'] / df['cases']

# 3. Select Features for the AI
# Notice: We are NOT using 'amount' as a primary driver. 
# We are using the Ratio. This protects the "Growth" client.
features = ['img_per_case_ratio', 'cases'] 

# 4. Train the Model
# contamination=0.05 means we expect about 5% of invoices to be weird.
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
model.fit(df[features])

# 5. Predict
df['anomaly_score'] = model.decision_function(df[features])
df['prediction'] = model.predict(df[features]) 

# Convert Prediction: -1 is Anomaly, 1 is Normal
df['status'] = df['prediction'].apply(lambda x: 'FLAGGED' if x == -1 else 'Approved')

# --- RESULTS ANALYSIS ---
print("\n--- DETECTION REPORT ---")

# Let's look at the "Slippery Vendor" (Client 103) specifically
print("\nClient 103 (The Fraudster):")
print(df[df['client_id'] == 103][['month', 'cases', 'images', 'img_per_case_ratio', 'status']])

# Let's look at the "Chaotic Startup" (Client 102) to make sure they are SAFE
print("\nClient 102 (The Startup):")
print(df[df['client_id'] == 102][['month', 'amount', 'img_per_case_ratio', 'status']].tail(3))

print("\nClient 101 (The Baseline):")
print(df[df['client_id'] == 101][['month', 'cases', 'images', 'img_per_case_ratio', 'status']].head(5))

# 5. Save the Brain
joblib.dump(model, "billing_guard_model.pkl")
print("Model saved as billing_guard_model.pkl")