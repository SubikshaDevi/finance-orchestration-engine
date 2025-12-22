import pandas as pd
import numpy as np
import random

# --- CONFIGURATION ---
# Base Rates (Simulating the Contract)
BASE_RATE = 50.0  # $ per Case
IMAGE_RATE = 2.0  # $ per Image

data = []

# --- SIMULATION LOOP (12 MONTHS) ---
for month in range(1, 13):
    
    # ---------------------------------------------------------
    # CLIENT 101: "Steady Eddie" (The Baseline)
    # Behavior: Consistent volume. Low variance.
    # ---------------------------------------------------------
    cases_101 = int(np.random.normal(100, 5))       # ~100 cases
    images_101 = int(cases_101 * np.random.normal(0.5, 0.05)) # ~0.5 images per case
    amount_101 = (cases_101 * BASE_RATE) + (images_101 * IMAGE_RATE)
    
    data.append({
        "client_id": 101,
        "persona": "Steady Eddie",
        "month": month,
        "cases": cases_101,
        "images": images_101,
        "amount": round(amount_101, 2),
        "is_anomaly": 0
    })

    # ---------------------------------------------------------
    # CLIENT 102: "Chaotic Startup" (The Growth Trap)
    # Behavior: Starts small, grows 20% every month.
    # Challenge: A simple "mean" check will fail because they are always "above average".
    # ---------------------------------------------------------
    # Base starts at 20 cases, grows 20% compounded monthly
    cases_102 = int(20 * (1.2 ** month)) 
    images_102 = int(cases_102 * 0.5)
    amount_102 = (cases_102 * BASE_RATE) + (images_102 * IMAGE_RATE)

    data.append({
        "client_id": 102,
        "persona": "Chaotic Startup",
        "month": month,
        "cases": cases_102,
        "images": images_102,
        "amount": round(amount_102, 2),
        "is_anomaly": 0  # TECHNICALLY NORMAL (Growth is not Fraud)
    })

    # ---------------------------------------------------------
    # CLIENT 103: "Slippery Vendor" (The Real Anomaly)
    # Behavior: Normal most months, but sneaks in bad bills in Month 6 & 11.
    # ---------------------------------------------------------
    cases_103 = int(np.random.normal(100, 5))
    
    # Logic: In Month 6 and 11, they charge for 10x images (The "Ratio Breaker")
    if month in [6, 11]:
        images_103 = cases_103 * 10  # 100 cases -> 1000 images (Suspicious!)
        is_bad = 1
    else:
        images_103 = int(cases_103 * 0.5) # Normal behavior
        is_bad = 0
        
    amount_103 = (cases_103 * BASE_RATE) + (images_103 * IMAGE_RATE)

    data.append({
        "client_id": 103,
        "persona": "Slippery Vendor",
        "month": month,
        "cases": cases_103,
        "images": images_103,
        "amount": round(amount_103, 2),
        "is_anomaly": is_bad
    })

# --- SAVE ---
df = pd.DataFrame(data)
df.to_csv("invoices_v2.csv", index=False)

print("--- Simulation Complete ---")
print(df.pivot(index="month", columns="persona", values="amount"))