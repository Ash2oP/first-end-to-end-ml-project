from database.db_config import db_connect
    
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from psycopg2 import extras
np.random.seed(42)

TOTAL_COUNT= 10000
NULL_RATIO = 0.05
NULL_COUNT = int(TOTAL_COUNT * NULL_RATIO)
VALID_COUNT = TOTAL_COUNT - NULL_COUNT
# Random Tenure Array, Our Anchor
tenure = np.random.randint(1,73, size=TOTAL_COUNT)

# Random Tech Support
bins = ["Yes", "No"]
tech_support = np.random.choice(bins,size=TOTAL_COUNT, replace=True)

# Customer Id
customer_id = ['CUST-' + str(x).zfill(4) for x in np.arange(TOTAL_COUNT)]

# Weighted Contracts
plans = ["Month-to-month", "One year", "Two year"]

long_term = np.random.choice(plans, size=TOTAL_COUNT, p=[0.1,0.4,0.5])
short_term = np.random.choice(plans, size=TOTAL_COUNT, p=[0.8,0.2,0.0])

contract = np.where(tenure > 24, long_term, short_term)

# Monthly Charges
base_charge = 70.00
mm_charge = 25.00 # $25 Monthly
yy_charge = 20.00 # $240 Yearly
yyyy_charge = 15.00 # 
ts_charge = 25.00

conditions = [
    contract == "Month-to-month",
    contract == "One year",
    contract == "Two year"
]
choices = [
    mm_charge,
    yy_charge,
    yyyy_charge
]
monthly_charges = np.full(TOTAL_COUNT, base_charge)
monthly_charges += np.select(conditions, choices, default=0)
monthly_charges += np.where(tech_support == "Yes", ts_charge, 0)

# Churn

# Weights
W1 = 1
W2 = 1
W3 = 0.5
W4 = 3

tenure_w = (tenure / max(tenure)) * W1
monthly_charges_w = (monthly_charges / max(monthly_charges)) * W2
tech_support_w = np.where(tech_support == "Yes", 1, 0) * W3
contract_w = np.select(conditions, choicelist=[1,0,-1], default=0) * W4


churn_risk = np.zeros(TOTAL_COUNT) - tenure_w - tech_support_w + contract_w + monthly_charges_w
n_scaler = MinMaxScaler()
churn_prob = n_scaler.fit_transform(churn_risk.reshape(-1, 1)).flatten()

random_roll = np.random.rand(TOTAL_COUNT)
churn = np.where(random_roll < churn_prob, "Yes", "No")

# Injecting NaNs
rand_idx1 = np.random.choice(TOTAL_COUNT, size=NULL_COUNT, replace=False)
rand_idx2 = np.random.choice(TOTAL_COUNT, size=NULL_COUNT, replace=False)
tenure = tenure.astype(dtype=float)
tenure[rand_idx1] = np.nan
monthly_charges[rand_idx2] = np.nan

df = pd.DataFrame({
    "customer_id" : customer_id,
    "monthly_charges" : monthly_charges,
    "tenure" : tenure, 
    "contract" : contract,
    "tech_support" : tech_support, 
    "churn" : churn
    })

# Replacing NaN with None
df.replace({np.nan : None}, inplace=True)

# Data Insertion
insert_query = """
INSERT INTO customers (customer_id, tenure, monthly_charges, contract, tech_support, churn)
VALUES %s
"""
data_tuples = [tuple(x) for x in df.to_numpy()]

conn = db_connect()

try:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE customers;")
        print("Table Cleared")
        extras.execute_values(cur, insert_query, data_tuples, page_size=1000)
        print("Data Inserted Successfuly")
    conn.commit()
    
except Exception as e:
    print(f"Data Not Inserted. Error : {e}")
    conn.rollback()
    
finally:
    if conn:
        conn.close()
        

