import pandas as pd
import re


df = pd.read_csv("D:/GK/Keesa/SMS-Parser/data/SMS-Banking-Transactions_Filtered12 - SMS-Banking-Transactions_Filtered12.csv")
print("📋 Columns in dataset:", df.columns.tolist())

""""
# Load the dataset
df = pd.read_csv("D:/GK/Keesa/SMS-Parser/data/SMS-Banking-Transactions_Filtered12 - SMS-Banking-Transactions_Filtered12.csv")

# Make sure the column exists
if 'sms' not in df.columns:
    raise ValueError("Column 'sms' not found in dataset")

# Normalize text
df['sms'] = df['sms'].astype(str).str.lower()

# Label mapping function
def get_label(sms):
    if re.search(r'\b(credited|received|deposited|got|cr)\b', sms):
        return 'credit'
    elif re.search(r'\b(debited|spent|sent|withdrawn|used|paid|dr)\b', sms):
        return 'debit'
    elif re.search(r'\b(available\s+balance|avl\s+bal|bal\s+rs\.?)\b', sms):
        return 'balance_update'
    elif re.search(r'\b(refunded|refund)\b', sms):
        return 'refund'
    elif re.search(r'\b(failed|declined|unsuccessful)\b', sms):
        return 'failed'
    elif re.search(r'\b(fraud|suspicious|not\s+you|unusual)\b', sms):
        return 'fraud'
    else:
        return 'unknown'

# Apply label fixing
df['label'] = df['sms'].apply(get_label)

# Remove unknowns if needed
df = df[df['label'] != 'unknown']

# Map to numerical values
label_map = {
    'credit': 0,
    'debit': 1,
    'balance_update': 2,
    'refund': 3,
    'failed': 4,
    'fraud': 5
}
df['label_num'] = df['label'].map(label_map)

# Save new file
df.to_csv("D:/GK/Keesa/SMS-Parser/data/sms_labeled_clean.csv", index=False)
print("✅ Relabeled dataset saved as 'sms_labeled_clean.csv'")
"""