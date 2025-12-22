"""
Ingestion Microservice - Runs independently
Deploy to Cloud Run or run standalone
"""

import os
import sys
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared import GCPPubSubBroker
from services.ingestion import DataIngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run Ingestion Service independently"""
    project_id = os.getenv('GCP_PROJECT_ID')
    bucket_name = os.getenv('GCP_BUCKET_NAME')
    
    # Set service account credentials from config folder if not already set
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        cred_path = os.path.join(os.path.dirname(__file__), 'config', 'service-account.json')
        if os.path.exists(cred_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path
            logger.info(f"🔑 Using service account: {cred_path}")
    
    if not project_id or not bucket_name:
        logger.error("❌ Missing GCP_PROJECT_ID or GCP_BUCKET_NAME environment variable")
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("🚀 Ingestion Microservice Starting")
    logger.info(f"📡 GCP Project: {project_id}")
    logger.info(f"📦 Cloud Storage Bucket: {bucket_name}")
    logger.info("=" * 70)
    
    # Initialize only what this service needs
    pubsub = GCPPubSubBroker(project_id)
    ingestion = DataIngestionService(pubsub, project_id, bucket_name)
    
    logger.info("✅ Ingestion service ready")
    logger.info("📥 Consuming from Pub/Sub topics...")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        # Keep the service alive (subscribers run in background threads)
        while True:
            time.sleep(10)
            stats = ingestion.get_stats()
            logger.info(f"📊 Ingested: {stats['total_ingested']} metrics | Timestamp: {stats['timestamp']}")
    
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("🛑 Ingestion service stopped")
        stats = ingestion.get_stats()
        logger.info(f"📊 Final stats: Total ingested: {stats['total_ingested']}")
        logger.info("=" * 70)


if __name__ == "__main__":
    main()
