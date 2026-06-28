from flask import Flask, request, render_template, redirect, url_for
import joblib, numpy as np, pandas as pd

app = Flask(__name__)
pipeline = joblib.load("models/champ_model.pkl")

@app.route("/predict", methods=["POST"])
def predict():
    data = pd.DataFrame([{
        "tenure":          int(request.form["tenure"]),
        "monthly_charges": float(request.form["monthly_charges"]),
        "contract":        request.form["contract"],
        "tech_support":    int(request.form["tech_support"]),
    }])
    pred = pipeline.predict(data)[0]
    result = "churn" if pred == 1 else "stay"
    return redirect(url_for("index") + f"?result={result}")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)