import pandas as pd
import json
# Open JSON data
with open("odb.json") as f:
    data = json.load(f)

# Create A DataFrame From the JSON Data
df = pd.DataFrame(data)