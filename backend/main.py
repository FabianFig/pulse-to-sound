from fastapi import FastAPI, Depends, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Pulse-to-Sound API")

# dependency: opens connection for the request and closes it after
def get_db():
    conn = psycopg2.connect(
        dbname="pulse_to_sound",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host="localhost"
    )
    try:
        yield conn
    finally:
        conn.close()

@app.get("/")
def root():
    return {"message": "Pulse-to-Sound API is active"}

# endpoint to get  list of all activities
@app.get("/activities")
def get_activities(conn=Depends(get_db)):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, type, start_date, distance FROM activities ORDER BY start_date DESC")
    results = cur.fetchall()
    cur.close()
    return results

# endpoint to get the time-series data for a specific ride
@app.get("/activities/{activity_id}/streams")
def get_activity_streams(activity_id: int, conn=Depends(get_db)):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT time_index, heartrate, altitude, velocity_smooth, lat, lng 
        FROM activity_streams 
        WHERE activity_id = %s 
        ORDER BY time_index ASC
    """, (activity_id,))
    
    streams = cur.fetchall()
    cur.close()

    if not streams:
        raise HTTPException(status_code=404, detail="Activity streams not found")
        
    return streams