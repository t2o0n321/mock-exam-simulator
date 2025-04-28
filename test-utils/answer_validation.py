import pandas as pd
import sys

csv_file = sys.argv[1]  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Print all values in the 'correct' column
print("Correct column values:", df["correct"].tolist())

# Find and print 2-based indices where 'correct' is nan
nan_indices = df.index[pd.isna(df["correct"])].tolist()
if nan_indices:
    # Add 2 to each index for 2-based indexing
    nan_indices_2_based = [idx + 2 for idx in nan_indices]
    print("Rows with nan in 'correct' column:", nan_indices_2_based)
else:
    print("No nan values found in 'correct' column.")