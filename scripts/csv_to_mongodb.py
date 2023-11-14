import pandas as pd
from pymongo import MongoClient

# MongoDB Atlas connection string
mongo_uri = "mongodb+srv://username:password@cluster0.nfvlsts.mongodb.net/store?retryWrites=true&w=majority"

# CSV file path
csv_file_path = r"C:\Users\adars\Downloads\timezones.csv"

# MongoDB database name
database_name = "store"

# MongoDB collection name
collection_name = "timezones"

# Read CSV file into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Convert DataFrame to JSON object with the first row as header
json_data = df.to_dict(orient='records')

# Connect to MongoDB Atlas
client = MongoClient(mongo_uri)

# Specify the name of the database
db = client[database_name]

# Specify the name of the collection
collection = db[collection_name]

# Insert data into MongoDB collection
collection.insert_many(json_data)

# Close MongoDB connection
client.close()

print("CSV data successfully loaded into MongoDB.")
