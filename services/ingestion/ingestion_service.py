"""
Data Ingestion Microservice
Consumes messages from GCP Pub/Sub, validates schema, stores to Cloud Storage
"""

from google.cloud import storage
from google.cloud import pubsub_v1
from google.api_core import exceptions as gexc
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionService:
    """Ingestion microservice - validates and stores to GCP Cloud Storage"""
    
    def __init__(self, pubsub, project_id, bucket_name):
        self.pubsub = pubsub
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.ingested_count = 0
        self.subscriber = pubsub_v1.SubscriberClient()
        self.streaming_futures = []
        
        # Initialize Cloud Storage
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)
        self._ensure_bucket_exists()
        
        logger.info(f"✅ Connected to GCS Bucket: {bucket_name}")
        
        # Subscribe to GCP Pub/Sub topics
        self._subscribe_and_consume()
    
    def _ensure_bucket_exists(self):
        """Use existing bucket; require it to be pre-created."""
        try:
            self.bucket = self.storage_client.get_bucket(self.bucket_name)
            logger.info(f"📦 Bucket exists: {self.bucket_name}")
        except gexc.NotFound:
            logger.error(
                f"❌ Bucket '{self.bucket_name}' not found. Create it first or grant bucket create permissions."
            )
            raise
        except gexc.Forbidden:
            logger.error(
                f"❌ No permission to access bucket '{self.bucket_name}'. Grant storage access to the service account."
            )
            raise
    
    def _subscribe_and_consume(self):
        """Ensure subscriptions exist and start streaming consumers."""
        subscription_configs = {
            'server-metrics-sub': (
                f'projects/{self.project_id}/topics/server-metrics',
                self._server_callback,
            ),
            'container-metrics-sub': (
                f'projects/{self.project_id}/topics/container-metrics',
                self._container_callback,
            ),
            'service-metrics-sub': (
                f'projects/{self.project_id}/topics/service-metrics',
                self._service_callback,
            ),
        }

        for sub_name, (topic_path, callback) in subscription_configs.items():
            sub_path = f'projects/{self.project_id}/subscriptions/{sub_name}'
            try:
                self.subscriber.create_subscription(request={'name': sub_path, 'topic': topic_path})
                logger.info(f"📬 Created subscription: {sub_name}")
            except gexc.AlreadyExists:
                logger.info(f"📬 Subscription exists: {sub_name}")

            future = self.subscriber.subscribe(sub_path, callback=callback)
            self.streaming_futures.append(future)
            logger.info(f"▶️  Streaming consumer started: {sub_name}")

    def _server_callback(self, message):
        try:
            data = json.loads(message.data.decode("utf-8"))
            self.ingest_server_metric(data)
            message.ack()
        except Exception as exc:
            logger.error(f"❌ Server metric ingest failed: {exc}")
            message.nack()

    def _container_callback(self, message):
        try:
            data = json.loads(message.data.decode("utf-8"))
            self.ingest_container_metric(data)
            message.ack()
        except Exception as exc:
            logger.error(f"❌ Container metric ingest failed: {exc}")
            message.nack()

    def _service_callback(self, message):
        try:
            data = json.loads(message.data.decode("utf-8"))
            self.ingest_service_metric(data)
            message.ack()
        except Exception as exc:
            logger.error(f"❌ Service metric ingest failed: {exc}")
            message.nack()
    
    def validate_schema(self, data: dict, required_fields: list) -> bool:
        """Validate data has required fields"""
        return all(field in data for field in required_fields)
    
    def ingest_server_metric(self, metric: dict):
        """Ingest server metric"""
        required = ["timestamp", "server_id", "cpu_percent", "memory_percent", "status"]
        if not self.validate_schema(metric, required):
            logger.error(f"❌ Invalid server metric schema: {metric}")
            return
        
        self._store_to_gcs("server_metrics.jsonl", metric)
        self.ingested_count += 1
    
    def ingest_container_metric(self, metric: dict):
        """Ingest container metric"""
        required = ["timestamp", "container_id", "cpu_percent", "memory_mb", "health"]
        if not self.validate_schema(metric, required):
            logger.error(f"❌ Invalid container metric schema: {metric}")
            return
        
        self._store_to_gcs("container_metrics.jsonl", metric)
        self.ingested_count += 1
    
    def ingest_service_metric(self, metric: dict):
        """Ingest service metric"""
        required = ["timestamp", "service_name", "error_rate_percent", "p95_response_time_ms"]
        if not self.validate_schema(metric, required):
            logger.error(f"❌ Invalid service metric schema: {metric}")
            return
        
        self._store_to_gcs("service_metrics.jsonl", metric)
        self.ingested_count += 1
    
    def _store_to_gcs(self, filename: str, data: dict):
        """Store data to GCS as JSONL (append by rewrite)."""
        try:
            blob = self.bucket.blob(filename)

            # Read existing content if present
            try:
                existing_content = blob.download_as_string().decode("utf-8")
            except Exception:
                existing_content = ""

            new_line = json.dumps(data) + "\n"
            updated_content = existing_content + new_line

            blob.upload_from_string(updated_content)
        except Exception as e:
            logger.error(f"❌ Failed to store metric: {e}")
    
    def get_stats(self) -> dict:
        """Get ingestion statistics"""
        return {
            "total_ingested": self.ingested_count,
            "timestamp": datetime.utcnow().isoformat()
        }
