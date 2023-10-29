import pandas as pd

# Load the wn.csv and recommend.csv files into DataFrames
wn_data = pd.read_csv('wn.csv')
recommend_data = pd.read_csv('recommendations.csv')

# Merge the DataFrames on the 'novel_id' column
merged_data = wn_data.merge(recommend_data, on='novel_id', how='left')

# Save the merged data to a new CSV file
merged_data.to_csv('wnM.csv', index=False)
print("sucessful")