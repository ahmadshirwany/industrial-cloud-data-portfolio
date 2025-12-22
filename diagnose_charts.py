#!/usr/bin/env python3
"""
Diagnostic script to check if database has data and why charts are empty
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("DASHBOARD CHARTS - EMPTY DATA DIAGNOSTIC")
print("="*70)

print("\n1. CHECKING DATABASE CONNECTION")
print("-" * 70)

try:
    from services.dashboard_api.database import SessionLocal
    db = SessionLocal()
    
    # Test connection
    result = db.execute("SELECT NOW()").fetchone()
    print(f"✓ Database connected: {result[0]}")
    
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    print("\nTo fix:")
    print("  1. Check DB_HOST, DB_USER, DB_PASSWORD environment variables")
    print("  2. Ensure PostgreSQL is running")
    print("  3. Verify credentials are correct")
    sys.exit(1)

print("\n2. CHECKING TABLE EXISTENCE")
print("-" * 70)

try:
    from sqlalchemy import text
    
    tables = ['server_metrics', 'service_metrics', 'container_metrics']
    for table in tables:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
        count = result[0]
        if count > 0:
            print(f"✓ {table:25} - {count} records")
        else:
            print(f"⚠ {table:25} - EMPTY (0 records)")
            
except Exception as e:
    print(f"✗ Error checking tables: {e}")
    sys.exit(1)

print("\n3. CHECKING DATA FRESHNESS")
print("-" * 70)

try:
    # Check server_metrics
    result = db.execute(text("SELECT MAX(timestamp) FROM server_metrics")).fetchone()
    if result[0]:
        print(f"✓ Latest server_metrics: {result[0]}")
        age = datetime.now(result[0].tzinfo) - result[0]
        print(f"  Age: {age.total_seconds():.0f} seconds old")
        if age.total_seconds() > 600:
            print(f"  ⚠ WARNING: Data is {int(age.total_seconds()/60)} minutes old")
    else:
        print("⚠ No server_metrics data found")
    
    # Check service_metrics
    result = db.execute(text("SELECT MAX(timestamp) FROM service_metrics")).fetchone()
    if result[0]:
        print(f"✓ Latest service_metrics: {result[0]}")
        age = datetime.now(result[0].tzinfo) - result[0]
        print(f"  Age: {age.total_seconds():.0f} seconds old")
        if age.total_seconds() > 600:
            print(f"  ⚠ WARNING: Data is {int(age.total_seconds()/60)} minutes old")
    else:
        print("⚠ No service_metrics data found")
        
except Exception as e:
    print(f"✗ Error checking data freshness: {e}")

print("\n4. CHECKING CHART QUERY COMPATIBILITY")
print("-" * 70)

try:
    # Test the CPU trends query
    query_text = """
        WITH time_buckets AS (
            SELECT 
                to_timestamp(FLOOR(EXTRACT(epoch FROM timestamp) / 300) * 300) as time_bucket,
                AVG(cpu_percent) as avg_cpu
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL '6 hours'
            GROUP BY FLOOR(EXTRACT(epoch FROM timestamp) / 300)
            ORDER BY time_bucket
        )
        SELECT time_bucket, avg_cpu FROM time_buckets
    """
    
    results = db.execute(text(query_text)).fetchall()
    if results:
        print(f"✓ CPU trends query returned {len(results)} data points")
        for i, row in enumerate(results[:3]):
            print(f"  [{i+1}] {row[0]} - {row[1]}")
        if len(results) > 3:
            print(f"  ... and {len(results)-3} more")
    else:
        print("⚠ CPU trends query returned 0 results")
        print("\nPossible causes:")
        print("  1. No data in server_metrics table")
        print("  2. All data is older than 6 hours")
        print("  3. Data may not be indexed by timestamp")
        
except Exception as e:
    print(f"✗ Error testing chart query: {e}")
    print(f"\nQuery that failed:")
    print(query_text)

print("\n5. RECOMMENDED ACTIONS")
print("-" * 70)

try:
    result = db.execute(text("SELECT COUNT(*) FROM server_metrics")).fetchone()
    server_count = result[0]
except:
    server_count = 0

if server_count == 0:
    print("""
✓ ACTION 1: Start Data Generation
   Run the telemetry generator to create test data:
   
   docker-compose up generator transformer
   
   This will:
   - Generate synthetic metrics every 30 seconds
   - Send to Google Pub/Sub
   - Transform and load into PostgreSQL
   
   Wait 2-3 minutes for data to accumulate, then refresh dashboard.

✓ ACTION 2: Or Insert Test Data Directly (for development)
   
   If you don't want to run the full pipeline, insert sample data:
   
   psql -h $DB_HOST -U $DB_USER -d telemetry -c "
   INSERT INTO server_metrics (timestamp, server_id, region, cpu_percent, 
                               memory_percent, disk_utilization, status)
   SELECT 
     NOW() - interval '5 minutes' * (row_number() over ()),
     'server-' || (random()*5)::int,
     'us-west-1',
     (random()*80)::numeric(5,2),
     (random()*75)::numeric(5,2),
     (random()*90)::numeric(5,2),
     'healthy'
   FROM generate_series(1, 100);"
   
✓ ACTION 3: Check Generator Logs
   
   docker logs telemetry-generator
   docker logs telemetry-transformer
   
   Look for any errors preventing data ingestion.
    """)
else:
    print(f"""
✓ Database has {server_count} records
✓ Check API endpoints directly:
   
   curl http://localhost:8000/api/analytics/cpu-trends?hours=6
   curl http://localhost:8000/api/analytics/memory-trends?hours=6
   curl http://localhost:8000/api/analytics/system-health
   
✓ If API returns data but charts don't show:
   
   1. Check browser console for errors (F12 → Console)
   2. Verify frontend is making requests correctly
   3. Check API CORS headers
   4. Reload page (Ctrl+F5)
    """)

db.close()

print("\n" + "="*70)
print("END DIAGNOSTIC")
print("="*70 + "\n")
