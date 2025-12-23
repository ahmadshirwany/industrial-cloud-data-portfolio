"""
Transformer Microservice - Runs independently
Extracts from Cloud Storage, Transforms, Loads to PostgreSQL
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

from services.transformer import DataTransformerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global transformer instance
transformer = None
transformer_thread = None


def run_transformer_loop():
    """Background thread running transformer ETL loop"""
    global transformer
    try:
        round_num = 0
        while True:
            round_num += 1
            logger.info(f"\n[{round_num:04d}] 🔄 Starting ETL cycle...")
            
            transformer.run_etl()
            
            stats = transformer.get_stats()
            logger.info(f"📊 Total transformed: {stats['total_transformed']}")
            logger.info("⏳ Waiting 60 seconds until next cycle...\n")
            
            time.sleep(60)
    except Exception as e:
        logger.error(f"Transformer error: {e}")


def create_app():
    """Create Flask app for Cloud Run"""
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'transformer',
            'total_transformed': transformer.get_stats()['total_transformed'] if transformer else 0
        }), 200
    
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'service': 'Industrial Cloud Transformer',
            'status': 'running',
            'description': 'Transforms telemetry data and loads to PostgreSQL database'
        }), 200
    
    return app


def main():
    """Run Transformer Service independently"""
    project_id = os.getenv('GCP_PROJECT_ID')
    bucket_name = os.getenv('GCP_BUCKET_NAME')
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', 5432),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    # Set service account credentials from config folder if not already set
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        cred_path = os.path.join(os.path.dirname(__file__), 'config', 'service-account.json')
        if os.path.exists(cred_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path
            logger.info(f"🔑 Using service account: {cred_path}")
    
    if not all([project_id, bucket_name, db_config['host'], db_config['database'], db_config['user'], db_config['password']]):
        logger.error("❌ Missing required environment variables")
        logger.error("Required: GCP_PROJECT_ID, GCP_BUCKET_NAME, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD")
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("🚀 Transformer Microservice Starting")
    logger.info(f"📡 GCP Project: {project_id}")
    logger.info(f"📦 Cloud Storage Bucket: {bucket_name}")
    logger.info(f"🗄️  PostgreSQL Database: {db_config['database']}")
    logger.info("=" * 70)
    
    try:
        # Initialize transformer service (global for thread)
        global transformer
        transformer = DataTransformerService(project_id, bucket_name, db_config)
        
        logger.info("✅ Transformer service ready")
        logger.info("🔄 Running ETL every 60 seconds...")
        
        # Start the transformer loop in a background daemon thread
        transformer_thread = threading.Thread(target=run_transformer_loop, daemon=True)
        transformer_thread.start()
        
        # Start Flask HTTP server (required by Cloud Run)
        app = create_app()
        port = int(os.getenv('PORT', 8000))
        logger.info(f"🌐 Starting Flask server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("🛑 Transformer service stopped")
        if transformer:
            stats = transformer.get_stats()
            logger.info(f"📊 Final stats: Total transformed: {stats['total_transformed']}")
            transformer.close()
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        if transformer:
            transformer.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
