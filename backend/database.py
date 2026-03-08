import os
import psycopg2
import json
from dotenv import load_dotenv
from psycopg2.extras import execute_values
load_dotenv()

conn = psycopg2.connect(
    dbname="pulse_to_sound",
    user="postgres",
    password=os.getenv("DB_PASSWORD"),
    host="localhost"
    )
cur = conn.cursor()

## ---- LAYER 2 ----

### Activities 
activity_path = "data/raw/activities"
a_filenames = os.listdir(activity_path)
activity_data = []

for file in a_filenames:
    if not file.endswith('.json'):
        continue
    
    filepath = os.path.join(activity_path, file)
    
    # opening and loading json
    with open(filepath, 'r') as f:
        data = json.load(f)
        activity_data.append(data)

if activity_data:
    print(f"Loaded {len(activity_data)} activities")
else:
    print("No JSON files found")

# Populating activities table
for activity in activity_data:
    activity_id = activity.get('id')
    name = activity.get('name')
    type = activity.get('type')
    start_date = activity.get('start_date')
    distance = activity.get('distance')
    moving_time = activity.get('moving_time')
    elapsed_time = activity.get('elapsed_time')
    total_elevation_gain = activity.get('total_elevation_gain')
    device_name = activity.get('device_name')
    external_id = activity.get('external_id')
    
    activities_insert_query = """
        INSERT INTO activities (id, name, type, start_date, distance, moving_time, elapsed_time, total_elevation_gain, device_name, external_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    cur.execute(activities_insert_query, (activity_id, name, type, start_date, distance, moving_time, elapsed_time, total_elevation_gain, device_name, external_id))
conn.commit()

### Streams
streams_path = "data/raw/streams"
s_filenames = os.listdir(streams_path)

# countners for tracking ingest progress and confirming the bulk load worked
processed_stream_files = 0
inserted_stream_rows = 0

# bulk insert query for time-series stream points into the actual target table
stream_insert_query = """
    INSERT INTO activity_streams (activity_id, time_index, altitude, heartrate, velocity_smooth, lat, lng)
    VALUES %s
"""

for file in s_filenames:
    if not file.endswith('_streams.json'):
        continue

    # Extract activity_id from filename so each stream row can reference activities.id (foreign key).
    activity_id_part = file.split('_')[0]
    if not activity_id_part.isdigit():
        print(f"Skipping malformed stream filename: {file}")
        continue

    activity_id = int(activity_id_part)
    filepath = os.path.join(streams_path, file)
    
    # opening and loading json
    with open(filepath, 'r') as f:
        data = json.load(f)

    # streams stored as "columnar" arrays in JSON
    # pull stream types needed for activity_streams
    time_data = data.get('time', {}).get('data', [])
    altitude_data = data.get('altitude', {}).get('data', [])
    heartrate_data = data.get('heartrate', {}).get('data', [])
    velocity_data = data.get('velocity_smooth', {}).get('data', [])
    latlng_data = data.get('latlng', {}).get('data', [])

    # time is required for row indexing
    if not time_data:
        continue

    # Padding optional streams to time length so zip includes every time point
    n = len(time_data)
    altitude_data = altitude_data if altitude_data else [None] * n
    heartrate_data = heartrate_data if heartrate_data else [None] * n
    velocity_data = velocity_data if velocity_data else [None] * n

    lat_data = [point[0] if isinstance(point, list) and len(point) == 2 else None for point in latlng_data]
    lng_data = [point[1] if isinstance(point, list) and len(point) == 2 else None for point in latlng_data]
    if not lat_data:
        lat_data = [None] * n
    if not lng_data:
        lng_data = [None] * n

    # Convert columnar arrays into row tuples for the insert
    # zip() to alight points by index across each stream
    rows_to_insert = [
        (activity_id, t, alt, hr, vel, lat, lng)
        for t, alt, hr, vel, lat, lng in zip(time_data, altitude_data, heartrate_data, velocity_data, lat_data, lng_data)
    ]

    if not rows_to_insert:
        continue

    # execute_values performs one bulk insert per file (much faster than row-by-row execute).
    execute_values(cur, stream_insert_query, rows_to_insert)
    processed_stream_files += 1
    inserted_stream_rows += len(rows_to_insert)

if processed_stream_files:
    print(f"Processed {processed_stream_files} stream files")
    print(f"Inserted {inserted_stream_rows} stream rows")
else:
    print("No valid stream files found")
    
conn.commit()

cur.close()
conn.close()