#!/usr/bin/env python

import json
import pickle
import sys

import pandas as pd
from sklearn.linear_model import LogisticRegression

input_csv = sys.argv[1]
input_batch = sys.argv[2]
output_model = sys.argv[3]
output_json = sys.argv[4]


df = pd.read_csv(input_csv)


X = df[["Age", "Glucose_mg_dL"]]
y = df["Diabetes"]
model = LogisticRegression()


model.fit(X, y)

with open(output_model, "wb") as file:
    pickle.dump(model, file)

acc = float(model.score(X, y))

data = {
    "batch_id": input_batch,
    "samples_trained": X.shape[0],
    "accuracy": acc,
    "intercept": float(model.intercept_[0]),
    "coefficients": {col: float(coef) for col, coef in zip(X.columns, model.coef_[0])},
}
with open(output_json, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)
