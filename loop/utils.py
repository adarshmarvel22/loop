# utils.py
import pandas as pd
from datetime import timedelta
from django.utils import timezone
from .models import *
from pymongo import MongoClient

# Connect to MongoDB
mongo_uri = "mongodb+srv://username:password@cluster0.nfvlsts.mongodb.net/store?retryWrites=true&w=majority"

import logging
# Configure logging
logger = logging.getLogger(__name__)

def remove_id_column(data_frame):
    if '_id' in data_frame.columns:
        data_frame.drop('_id', axis=1, inplace=True)

def generate_report(report_id):
    client = MongoClient(mongo_uri)
    db = client['store']
    # Fetch data from MongoDB
    store_status_data = pd.DataFrame(list(db['store_status'].find()))
    remove_id_column(store_status_data)
    business_hours_data = pd.DataFrame(list(db['business_hours'].find()))
    remove_id_column(business_hours_data)
    timezones_data = pd.DataFrame(list(db['timezones'].find()))
    remove_id_column(timezones_data)

    logging.info(store_status_data.isna().sum())
    logging.info(business_hours_data.isna().sum())
    logging.info(timezones_data.isna().sum())

    # Extract unique store_ids from store_status
    logging.info("Extract unique store_ids from store_status")
    all_store_ids = set(store_status_data['store_id'])

    # Extract unique store_ids from business_hours and timezones
    existing_store_ids_business_hours = set(business_hours_data['store_id'])
    existing_store_ids_timezones = set(timezones_data['store_id'])

    logging.info("Find missing store_ids")
    # Find missing store_ids
    missing_store_ids_business_hours = all_store_ids - existing_store_ids_business_hours
    missing_store_ids_timezones = all_store_ids - existing_store_ids_timezones

    # Create DataFrames with missing store_ids and empty values
    logging.info("Create DataFrames with missing store_ids and empty values")
    missing_data_business_hours = pd.DataFrame({'store_id': list(missing_store_ids_business_hours)})
    missing_data_timezones = pd.DataFrame({'store_id': list(missing_store_ids_timezones)})

    logging.info("Concatenate missing data with existing data")
    # Concatenate missing data with existing data
    business_hours_data = pd.concat([business_hours_data, missing_data_business_hours], ignore_index=True)
    timezones_data = pd.concat([timezones_data, missing_data_timezones], ignore_index=True)

    logging.info("Merge data")
    # Merge data
    merged_data = pd.merge(store_status_data, business_hours_data, on='store_id', how='left')
    merged_data = pd.merge(merged_data, timezones_data, on='store_id', how='left')

    logging.info("Assume default values for missing data")
    # Assume default values for missing data
    merged_data = merged_data.fillna({'start_time_local': '00:00:00', 'end_time_local': '23:59:59'})
    merged_data = merged_data.fillna({'timezone_str': 'America/Chicago'})
    merged_data = merged_data.fillna({'day': 0})

    logging.info("Convert timestamps to datetime")
    logging.info(merged_data.isna().sum())
    logging.info(merged_data.head())
    # Convert timestamps to datetime
    # merged_data['timestamp_utc'] = pd.to_datetime(merged_data['timestamp_utc'])
    # Remove 'UTC' from 'timestamp_utc' column
    merged_data['timestamp_utc'] = merged_data['timestamp_utc'].str.replace(' UTC', '')

    # Convert 'timestamp_utc' column to datetime
    merged_data['timestamp_utc'] = pd.to_datetime(merged_data['timestamp_utc'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
    merged_data['start_time_local'] = pd.to_datetime(merged_data['start_time_local'])
    merged_data['end_time_local'] = pd.to_datetime(merged_data['end_time_local'])

    logging.info("Fill missing values in business_hours and timezones")
    # Fill missing values in 'business_hours' and 'timezones'
    merged_data['start_time_local'] = merged_data['start_time_local'].fillna(pd.Timestamp('00:00:00'))
    merged_data['end_time_local'] = merged_data['end_time_local'].fillna(pd.Timestamp('23:59:59'))
    merged_data['timezone_str'] = merged_data['timezone_str'].fillna('America/Chicago')

    logging.info("Filter data within business hours")
    # Filter data within business hours
    merged_data = merged_data[(merged_data['timestamp_utc'].dt.time >= merged_data['start_time_local'].dt.time) &
                              (merged_data['timestamp_utc'].dt.time <= merged_data['end_time_local'].dt.time)]
    
    logging.info("Interpolate uptime and downtime")
    # Interpolate uptime and downtime
    merged_data['uptime'] = merged_data['status'].apply(lambda x: 1 if x == 'active' else 0)
    merged_data['downtime'] = merged_data['status'].apply(lambda x: 1 if x == 'inactive' else 0)

    # Group by store_id and apply interpolation logic
    report_data = merged_data.groupby('store_id').apply(interpolate_data).reset_index(drop=True)
    logging.info("Extract unique store_ids from business_hours and timezones")

    # # Save report data to the new table
    csv_content = report_data.to_csv(index=False)

    # Insert data into MongoDB
    report_info = {
        'report_id': report_id,  # Replace with the actual report_id
        'status': 'Complete',
        'csv_data': csv_content,
    }

    # Insert report_info into MongoDB
    db[report_id].insert_one(report_info)

    # Close MongoDB connection
    client.close()

def interpolate_data(group):
    current_timestamp = group['timestamp_utc'].max()

    # Interpolate data for the entire business hours interval
    business_hours_interval = pd.date_range(group['start_time_local'].iloc[0], group['end_time_local'].iloc[0], freq='H')
    interpolated_data = pd.DataFrame({'timestamp_utc': business_hours_interval})
    interpolated_data['uptime'] = 0
    interpolated_data['downtime'] = 0

    for _, row in group.iterrows():
        time_difference = (current_timestamp - row['timestamp_utc']).total_seconds() / 3600
        interpolated_data['uptime'] += row['uptime'] * (1 - time_difference)
        interpolated_data['downtime'] += row['downtime'] * (1 - time_difference)

    # Calculate total uptime and downtime
    total_uptime_last_hour = interpolated_data['uptime'].sum()
    total_downtime_last_hour = interpolated_data['downtime'].sum()
    total_uptime_last_day = total_uptime_last_hour * 24
    total_downtime_last_day = total_downtime_last_hour * 24
    total_uptime_last_week = total_uptime_last_day * 7
    total_downtime_last_week = total_downtime_last_day * 7

    return pd.Series({
        'store_id': group['store_id'].iloc[0],
        'uptime_last_hour': total_uptime_last_hour,
        'uptime_last_day': total_uptime_last_day,
        'uptime_last_week': total_uptime_last_week,
        'downtime_last_hour': total_downtime_last_hour,
        'downtime_last_day': total_downtime_last_day,
        'downtime_last_week': total_downtime_last_week
    })
