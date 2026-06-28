import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
from database.db_config import db_connect

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
import warnings

MODEL_FILE = os.path.join(ROOT_DIR, "models", "champ_model.pkl")

def build_processing_pipeline(num_attr, cat_attr):
    
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", MinMaxScaler())
    ])
    
    cat_pipeline = Pipeline([
        ("one_hot", OneHotEncoder(sparse_output=False, handle_unknown="ignore"))
    ])
    
    full_pipeline = ColumnTransformer([
        ("num", num_pipeline, num_attr),
        ("cat", cat_pipeline, cat_attr)
    ])
    
    return full_pipeline

def build_champion_model(x_train, y_train, preprocessor):
    
    param_grid_lr = {
        'model__C': [0.001, 0.01, 0.1, 1, 10, 100],  
        'model__penalty': ['l1', 'l2'],              
        'model__solver': ['liblinear', 'saga']       
    }
    
    grid_search_lr = GridSearchCV(
        estimator= Pipeline([
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=1000))
            ]),
        param_grid=param_grid_lr, 
        cv=5, 
        scoring='accuracy'
        )
    grid_search_lr.fit(x_train, y_train)
    return grid_search_lr.best_estimator_

os.makedirs('models', exist_ok=True)

if not os.path.exists(MODEL_FILE):
    conn = db_connect()
    df = pd.read_sql_query("SELECT * FROM customers", conn, index_col="customer_id")
    conn.close()
    
    bin_map = {"Yes" : 1, "No" : 0}
    df["churn"] = df["churn"].map(bin_map)
    df["tech_support"] = df["tech_support"].map(bin_map)
    
    strata_split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_i, test_i in strata_split.split(df, df["churn"]):
        df_train = df.iloc[train_i].copy()
        df_test = df.iloc[test_i].copy()
        
    y_train = df_train["churn"].copy()
    y_test = df_test["churn"].copy()
    x_train = df_train.drop(columns=["churn"]).copy()
    x_test = df_test.drop(columns=["churn"]).copy()
    
    num_attr = ["tenure", "monthly_charges"]
    cat_attr = ["contract"] 
    
    pre_processing_pipeline = build_processing_pipeline(num_attr, cat_attr)       
    
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        
        champion_model = build_champion_model(x_train, y_train, pre_processing_pipeline)
    
    joblib.dump(champion_model, MODEL_FILE)
    
    predictions = champion_model.predict(x_test)
    print(classification_report(y_test, predictions))
    