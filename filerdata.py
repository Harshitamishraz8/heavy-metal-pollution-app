import pandas as pd

# Excel file load karo
df = pd.read_excel("final_nhs-wq_pre_2023_compressed.xlsx")

# Dash ("-") ko NaN me convert karo
df = df.replace("-", pd.NA)

# Sirf wahi rows rakho jisme koi missing ya fake value na ho
df_clean = df.dropna(how='any')

# Cleaned data save as CSV
df_clean.to_csv("filtered_output.csv", index=False)

print("Filtering complete")
print(f"Original rows: {len(df)}")
print(f"Filtered rows: {len(df_clean)}")
