import pandas as pd

print("Examining Excel file structure...")
df = pd.read_excel("Salesforce_Complete_Metadata.xlsx")
print("Columns in Excel file:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())