"""
Ingestion Microservice - Runs independently
Deploy to Cloud Run as a service
"""

import os
import sys
import time
import logging
import threading
from flask import Flask, jsonify

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared import GCPPubSubBroker
from services.ingestion import DataIngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global ingestion instance
ingestion = None
ingestion_thread = None


def run_ingestion_loop():
    """Background thread running ingestion loop"""
    global ingestion
    
    try:
        while True:
            time.sleep(10)
            stats = ingestion.get_stats()
            logger.info(f"📊 Ingested: {stats['total_ingested']} metrics | Timestamp: {stats['timestamp']}")
    except Exception as e:
        logger.error(f"Ingestion error: {e}")


def create_app():
    """Create Flask app for Cloud Run"""
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'ingestion',
            'total_ingested': ingestion.get_stats()['total_ingested'] if ingestion else 0
        }), 200
    
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'service': 'Industrial Cloud Ingestion',
            'status': 'running',
            'description': 'Consumes telemetry data from Pub/Sub and stores to Cloud Storage'
        }), 200
    
    return app


def main():
    """Run Ingestion Service independently"""
    global ingestion, ingestion_thread
    
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
    
    # Initialize ingestion service
    pubsub = GCPPubSubBroker(project_id)
    ingestion = DataIngestionService(pubsub, project_id, bucket_name)
    
    logger.info("✅ Ingestion service ready")
    logger.info("📥 Consuming from Pub/Sub topics...")
    
    # Start monitoring thread
    ingestion_thread = threading.Thread(target=run_ingestion_loop, daemon=True)
    ingestion_thread.start()
    
    # Start Flask app for Cloud Run
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"🌐 Starting HTTP server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("🛑 Ingestion service stopped")
        if ingestion:
            stats = ingestion.get_stats()
            logger.info(f"📊 Final stats: Total ingested: {stats['total_ingested']}")
        logger.info("=" * 70)
