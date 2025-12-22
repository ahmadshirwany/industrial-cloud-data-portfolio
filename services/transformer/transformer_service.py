"""
Data Transformer Microservice (ETL)
Consumes from Cloud Storage, transforms data, loads to PostgreSQL
"""

from google.cloud import storage
from google.cloud import pubsub_v1
from google.api_core import exceptions as gexc
import psycopg2
from psycopg2.extras import execute_values
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataTransformerService:
    """ETL microservice - Extract from GCS, Transform, Load to PostgreSQL"""
    
    def __init__(self, project_id, bucket_name, db_config):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.db_config = db_config
        self.transformed_count = 0
        
        # Initialize Cloud Storage
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)
        
        logger.info(f"✅ Connected to GCS Bucket: {bucket_name}")
        
        # Connect to PostgreSQL
        self._connect_db()
        self._create_tables()
        
        logger.info("✅ Transformer service initialized")
    
    def _connect_db(self):
        """Connect to Cloud SQL PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config.get('port', 5432),
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.conn.autocommit = False
            logger.info(f"✅ Connected to PostgreSQL: {self.db_config['database']}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            raise
    
    def _create_tables(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Server metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                server_id VARCHAR(50) NOT NULL,
                region VARCHAR(50),
                environment VARCHAR(50),
                cpu_percent DECIMAL(5,2),
                memory_percent DECIMAL(5,2),
                memory_used_gb DECIMAL(10,2),
                memory_total_gb INTEGER,
                disk_used_gb INTEGER,
                disk_total_gb INTEGER,
                disk_utilization DECIMAL(5,2),
                status VARCHAR(20),
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for server_metrics
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_server_timestamp ON server_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_server_id ON server_metrics(server_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_server_environment ON server_metrics(environment)")
        
        # Container metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS container_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                container_id VARCHAR(50) NOT NULL,
                service_name VARCHAR(100),
                version VARCHAR(50),
                environment VARCHAR(50),
                cpu_percent DECIMAL(5,2),
                memory_mb INTEGER,
                memory_limit_mb INTEGER,
                memory_utilization DECIMAL(5,2),
                requests_per_sec INTEGER,
                response_time_ms DECIMAL(10,2),
                error_count INTEGER,
                restart_count INTEGER,
                health VARCHAR(20),
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for container_metrics
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_container_timestamp ON container_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_container_id ON container_metrics(container_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_container_service_name ON container_metrics(service_name)")
        
        # Service metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                service_name VARCHAR(100) NOT NULL,
                version VARCHAR(50),
                environment VARCHAR(50),
                region VARCHAR(50),
                total_requests INTEGER,
                failed_requests INTEGER,
                success_rate DECIMAL(5,2),
                error_rate_percent DECIMAL(5,2),
                avg_response_time_ms DECIMAL(10,2),
                p95_response_time_ms DECIMAL(10,2),
                instances_running INTEGER,
                cpu_avg_percent DECIMAL(5,2),
                memory_avg_percent DECIMAL(5,2),
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for service_metrics
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_timestamp ON service_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_name ON service_metrics(service_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_environment ON service_metrics(environment)")
        
        self.conn.commit()
        logger.info("📋 Database tables ready")
    
    def extract_from_gcs(self, filename):
        """Extract JSONL data from Cloud Storage"""
        try:
            blob = self.bucket.blob(filename)
            content = blob.download_as_string().decode('utf-8')
            
            # Parse JSONL (one JSON per line)
            records = []
            for line in content.strip().split('\n'):
                if line:
                    records.append(json.loads(line))
            
            logger.info(f"📥 Extracted {len(records)} records from {filename}")
            return records
        except Exception as e:
            logger.error(f"❌ Failed to extract from {filename}: {e}")
            return []
    
    def transform_server_metrics(self, records):
        """Transform server metrics"""
        transformed = []
        for record in records:
            # Calculate derived metrics
            disk_util = (record['disk_used_gb'] / record['disk_total_gb'] * 100) if record['disk_total_gb'] > 0 else 0
            
            transformed.append({
                'timestamp': record['timestamp'].replace('Z', ''),
                'server_id': record['server_id'],
                'region': record['region'],
                'environment': record['environment'],
                'cpu_percent': record['cpu_percent'],
                'memory_percent': record['memory_percent'],
                'memory_used_gb': record['memory_used_gb'],
                'memory_total_gb': record['memory_total_gb'],
                'disk_used_gb': record['disk_used_gb'],
                'disk_total_gb': record['disk_total_gb'],
                'disk_utilization': round(disk_util, 2),
                'status': record['status']
            })
        
        return transformed
    
    def transform_container_metrics(self, records):
        """Transform container metrics"""
        transformed = []
        for record in records:
            # Calculate memory utilization
            mem_util = (record['memory_mb'] / record['memory_limit_mb'] * 100) if record['memory_limit_mb'] > 0 else 0
            
            transformed.append({
                'timestamp': record['timestamp'].replace('Z', ''),
                'container_id': record['container_id'],
                'service_name': record['service_name'],
                'version': record['version'],
                'environment': record['environment'],
                'cpu_percent': record['cpu_percent'],
                'memory_mb': record['memory_mb'],
                'memory_limit_mb': record['memory_limit_mb'],
                'memory_utilization': round(mem_util, 2),
                'requests_per_sec': record['requests_per_sec'],
                'response_time_ms': record['response_time_ms'],
                'error_count': record['error_count'],
                'restart_count': record['restart_count'],
                'health': record['health']
            })
        
        return transformed
    
    def transform_service_metrics(self, records):
        """Transform service metrics"""
        transformed = []
        for record in records:
            # Calculate success rate
            success_rate = ((record['total_requests'] - record['failed_requests']) / record['total_requests'] * 100) if record['total_requests'] > 0 else 100
            
            transformed.append({
                'timestamp': record['timestamp'].replace('Z', ''),
                'service_name': record['service_name'],
                'version': record['version'],
                'environment': record['environment'],
                'region': record['region'],
                'total_requests': record['total_requests'],
                'failed_requests': record['failed_requests'],
                'success_rate': round(success_rate, 2),
                'error_rate_percent': record['error_rate_percent'],
                'avg_response_time_ms': record['avg_response_time_ms'],
                'p95_response_time_ms': record['p95_response_time_ms'],
                'instances_running': record['instances_running'],
                'cpu_avg_percent': record['cpu_avg_percent'],
                'memory_avg_percent': record['memory_avg_percent']
            })
        
        return transformed
    
    def load_to_postgres(self, table_name, records):
        """Load transformed data to PostgreSQL"""
        if not records:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Get column names from first record
            columns = list(records[0].keys())
            
            # Build INSERT query
            insert_query = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES %s
            """
            
            # Prepare values
            values = [tuple(record[col] for col in columns) for record in records]
            
            # Bulk insert
            execute_values(cursor, insert_query, values)
            self.conn.commit()
            
            self.transformed_count += len(records)
            logger.info(f"✅ Loaded {len(records)} records to {table_name}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Failed to load to {table_name}: {e}")
    
    def run_etl(self):
        """Run full ETL pipeline"""
        logger.info("🔄 Starting ETL pipeline...")
        
        # Extract, Transform, Load - Server Metrics
        server_records = self.extract_from_gcs("server_metrics.jsonl")
        if server_records:
            transformed = self.transform_server_metrics(server_records)
            self.load_to_postgres("server_metrics", transformed)
        
        # Extract, Transform, Load - Container Metrics
        container_records = self.extract_from_gcs("container_metrics.jsonl")
        if container_records:
            transformed = self.transform_container_metrics(container_records)
            self.load_to_postgres("container_metrics", transformed)
        
        # Extract, Transform, Load - Service Metrics
        service_records = self.extract_from_gcs("service_metrics.jsonl")
        if service_records:
            transformed = self.transform_service_metrics(service_records)
            self.load_to_postgres("service_metrics", transformed)
        
        logger.info(f"✅ ETL pipeline complete: {self.transformed_count} total records")
    
    def get_stats(self):
        """Get transformation statistics"""
        return {
            "total_transformed": self.transformed_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Database connection closed")
