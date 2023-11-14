# tasks.py (Celery task for report generation)
from celery import shared_task
from .utils import generate_report  # Implement the report generation logic in a separate utility function
import random
import json
from pymongo import MongoClient

# Connect to MongoDB
mongo_uri = "mongodb+srv://username:password@cluster0.nfvlsts.mongodb.net/store?retryWrites=true&w=majority"

client = MongoClient(mongo_uri)
db = client['store']

import logging
# Configure logging
logger = logging.getLogger(__name__)

@shared_task
def generate_report_task(report_id):
    try:
        # Generate report content
        csv_content = generate_report(report_id)

        # Update report_info into MongoDB with the given report_id
        report_info = {
            'report_id': report_id,
            'status': 'Completed',
            'csv_data': csv_content,
        }
        db[report_id].update_one({'report_id': report_id}, {'$set': report_info}, upsert=True)

    except Exception as e:
        # Handle exceptions as needed
        print(f"Error generating report: {str(e)}")
    finally:
        # Close MongoDB connection
        client.close()
    logging.info(f"Report with report_id={report_id} created or updated successfully.")

def generate_random_string(length=10):
    # Generate a random string for the report_id
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(length))
