#!/usr/bin/env python
import json
import sys

import pandas as pd

raw_csv = sys.argv[1]
cleaned_csv = sys.argv[2]
qc_json = sys.argv[3]

df = pd.read_csv(raw_csv, na_values=["NA", "ERROR", "missing", ""])
initial_rows = len(df)

df["Hemolysis_Index"] = pd.to_numeric(df["Hemolysis_Index"], errors="coerce")
df["Hemolysis_Index"] = df["Hemolysis_Index"].astype(float)
mean_hemolysis = df["Hemolysis_Index"].mean()
status = "REJECTED_HEMOLYSIS" if mean_hemolysis > 100.0 else "PASSED"


df["Glucose_mg_dL"] = pd.to_numeric(df["Glucose_mg_dL"], errors="coerce")
df = df[df["Glucose_mg_dL"].between(20.0, 500.0, inclusive="both")]


df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["Age"] = df["Age"].fillna(df["Age"].median())

df["Age"] = df["Age"].astype(int)
df["Diabetes"] = df["Diabetes"].astype(int)

cleaned_rows = len(df)

df.to_csv(cleaned_csv, index=False)


with open(qc_json, "w", encoding="utf-8") as file:
    json.dump(
        {
            "status": status,
            "initial_rows": initial_rows,
            "cleaned_rows": cleaned_rows,
            "mean_hemolysis": mean_hemolysis,
        },
        file,
        indent=4,
    )
