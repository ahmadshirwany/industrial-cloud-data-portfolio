"""
Transformer Microservice - Runs independently
Extracts from Cloud Storage, Transforms, Loads to PostgreSQL
"""

import os
import sys
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.transformer import DataTransformerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        # Initialize transformer service
        transformer = DataTransformerService(project_id, bucket_name, db_config)
        
        logger.info("✅ Transformer service ready")
        logger.info("🔄 Running ETL every 60 seconds...")
        logger.info("Press Ctrl+C to stop\n")
        
        round_num = 0
        while True:
            round_num += 1
            logger.info(f"\n[{round_num:04d}] 🔄 Starting ETL cycle...")
            
            transformer.run_etl()
            
            stats = transformer.get_stats()
            logger.info(f"📊 Total transformed: {stats['total_transformed']}")
            logger.info("⏳ Waiting 60 seconds until next cycle...\n")
            
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("🛑 Transformer service stopped")
        if 'transformer' in locals():
            stats = transformer.get_stats()
            logger.info(f"📊 Final stats: Total transformed: {stats['total_transformed']}")
            transformer.close()
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        if 'transformer' in locals():
            transformer.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
