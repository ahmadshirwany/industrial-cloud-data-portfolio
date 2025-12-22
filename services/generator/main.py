"""
Generator Microservice - Runs independently
Deploy to Cloud Run or run standalone
"""

import os
import sys
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared import GCPPubSubBroker
from services.generator import TelemetryGeneratorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run Generator Service independently"""
    project_id = os.getenv('GCP_PROJECT_ID')
    
    # Set service account credentials from config folder if not already set
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        cred_path = os.path.join(os.path.dirname(__file__), 'config', 'service-account.json')
        if os.path.exists(cred_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path
            logger.info(f"🔑 Using service account: {cred_path}")
    
    if not project_id:
        logger.error("❌ Missing GCP_PROJECT_ID environment variable")
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("🚀 Generator Microservice Starting")
    logger.info(f"📡 GCP Project: {project_id}")
    logger.info("=" * 70)
    
    # Initialize only what this service needs
    pubsub = GCPPubSubBroker(project_id)
    generator = TelemetryGeneratorService(pubsub)
    
    logger.info("✅ Generator service ready")
    logger.info("📤 Publishing metrics every 30 seconds...")
    logger.info("⚙️  Optimized for cost: 2,880 records/day (vs 17,280 baseline)")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        round_num = 0
        while True:
            round_num += 1
            metrics = generator.generate_and_publish()
            
            logger.info(f"[{round_num:04d}] 📤 Published to Pub/Sub")
            logger.info(f"  Server:    {metrics['server']['server_id']} - CPU: {metrics['server']['cpu_percent']}%")
            logger.info(f"  Container: {metrics['container']['container_id']} - Req/s: {metrics['container']['requests_per_sec']}")
            logger.info(f"  Service:   {metrics['service']['service_name']} - Error: {metrics['service']['error_rate_percent']}%")
            logger.info("")
            
            time.sleep(30)
    
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("🛑 Generator service stopped")
        stats = generator.get_stats()
        logger.info(f"📊 Total metrics generated: {stats['total_generated']}")
        logger.info("=" * 70)


if __name__ == "__main__":
    main()
