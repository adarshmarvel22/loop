# Create your views here.
# views.py
from django.shortcuts import render,HttpResponse
from .utils import generate_report
from pymongo import MongoClient

# views.py
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .tasks import generate_report_task  #  Celery task for report generation

# Connect to MongoDB
mongo_uri = "mongodb+srv://username:password@cluster0.nfvlsts.mongodb.net/store?retryWrites=true&w=majority"

import logging
# Configure logging
logger = logging.getLogger(__name__)

import random
def generate_random_string(length=10):
    # Generate a random string for the report_id
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(length))

def home(request):
    # Pass data to the template
    context = {'app': 'Restaurant Monitoring System'}
    
    # Render the template with the provided context
    return render(request, 'home.html', context)

# @api_view(['GET'])
def trigger_report_view(request):
    client = MongoClient(mongo_uri)
    db = client['store']
    # Trigger the report generation task
    report_id = generate_random_string()
    # generate_report_task.delay(report_id)  # Use Celery to run the report generation task asynchronously
    generate_report(report_id)
    
    logging.info(f"Report with report_id={report_id} created or updated successfully.")
    client.close()
    return JsonResponse({'report_id': report_id})

# @api_view(['GET'])
def get_report(request, report_id):
    try:
        client = MongoClient(mongo_uri)
        db = client['store']
        # Assuming 'report_id' is a string
        report_info = db[report_id].find_one({'report_id': report_id})

        if report_info and report_info['status'] == "Complete":
            # Return the CSV file along with the status
            response_data = {
                'status': 'Complete',
                'csv_data': report_info['csv_data'],
            }
        elif report_info and report_info['status'] == "Running":
            # Return the status if report generation is still running
            response_data = {'status': 'Running'}
        else:
            # Report not found
            response_data = {'status': 'Report not found'}

        return JsonResponse(response_data)

    except Exception as e:
        # Handle exceptions as neededs
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Close MongoDB connection
        client.close()