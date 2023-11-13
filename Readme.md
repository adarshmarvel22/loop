# Restaurant Monitoring System

## Technical Details

### Technologies Used

- Django (Django Rest Framework)
- Celery
- Redis
- MongoDB

### Database

- MongoDB is used to store the CSV data.

### API Endpoints

1. **/trigger_report Endpoint:**
   - Method: `POST`
   - Triggers the Celery task for report generation.
   - Returns: `{ "report_id": "random_string" }`

2. **/get_report Endpoint:**
   - Method: `GET`
   - Input: `{ "report_id": "random_string" }`
   - Returns:
      - If the report generation is not complete: `{ "status": "Running" }`
      - If the report generation is complete: `{ "status": "Complete", "csv_data": "CSV_file_content" }`

### Celery Task

- The Celery task is responsible for generating the report asynchronously.
- It processes the CSV data, performs calculations, and stores the result in the MongoDB database.

### How to Run

1. Install required Python packages:

   ```bash
   pip install django djangorestframework celery redis pymongo
   ```

2. Start the MongoDB server.

3. Run Django migrations:

   ```bash
   python manage.py migrate
   ```

4. Start the Celery worker:

   ```bash
   celery -A your_project_name worker -l info
   ```

5. Start the Django development server:

   ```bash
   python manage.py runserver
   ```

6. Use the provided API endpoints to trigger and get the report.

---

Feel free to customize the implementation based on your specific project structure and requirements.

# Django-DRF Restaurant Monitoring System

## Overview

This document provides an overview and documentation for a Django-DRF (Django Rest Framework) based app designed to monitor restaurant online status. The app includes Celery for asynchronous task execution, Redis for task messaging, and MongoDB as the database to store relevant data.



- **`myproject/`**: Django project folder.
- **`loop/`**: Django app folder.
- **`migrations/`**: Django migrations folder.

## Django App Components

### `views.py`

Contains Django-DRF views for triggering and retrieving the report.

### `urls.py`

Defines the URLs for the Django app.

### `tasks.py`

Includes Celery task (`generate_report_task`) for generating reports asynchronously.

### `utils.py`

Contains utility functions, such as data extraction and report generation logic.

## Installation and Setup

1. Install required packages:

   ```bash
   pip install django djangorestframework celery redis pymongo
   ```

2. Start the MongoDB server.

3. Run Django migrations:

   ```bash
   python manage.py migrate
   ```

4. Start the Celery worker:

   ```bash
   celery -A myproject worker -l info
   ```

5. Start the Django development server:

   ```bash
   python manage.py runserver
   ```

## API Endpoints

1. **`/trigger_report/` Endpoint:**
   - Method: `POST`
   - Triggers the Celery task for report generation.
   - Returns: `{ "report_id": "random_string" }`

2. **`/get_report/<str:report_id>/` Endpoint:**
   - Method: `GET`
   - Input: `{ "report_id": "random_string" }`
   - Returns:
      - If the report generation is not complete: `{ "status": "Running" }`
      - If the report generation is complete: `{ "status": "Complete", "csv_data": "CSV_file_content" }`

## Celery Task (`tasks.py`)

The Celery task (`generate_report_task`) updates the status, generates the report, and stores the result in MongoDB.

## Report Generation Logic (`utils.py`)

The `generate_report` function extracts data from MongoDB, processes missing values, performs calculations, and stores the report in the MongoDB database.

### Data Processing Steps:

1. Extract data from MongoDB collections (`store_status`, `business_hours`, `timezones`).
2. Handle missing data in `business_hours` and `timezones`.
3. Convert timestamps to datetime format.
4. Filter data within business hours.
5. Interpolate uptime and downtime based on available data.
6. Extrapolate values for the entire business hours interval.
7. Save the report to the MongoDB collection (`report_table`).

## Report Generation Task (`tasks.py`)

The `generate_report_task` function updates the status of the report to "Running" and triggers the report generation logic.

## Logging

The app uses Python logging to provide information about the execution flow. Logs are configured in `tasks.py`.

## MongoDB Connection

The app connects to MongoDB using the provided URI and interacts with the `store` database.

## Conclusion

This Django-DRF app, integrated with Celery, Redis, and MongoDB, provides a scalable solution for monitoring restaurant online status and generating insightful reports. The app can be extended and customized based on specific project requirements.

---

Feel free to modify the documentation according to your specific needs and project structure.