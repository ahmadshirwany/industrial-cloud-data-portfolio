"""
Generator Microservice - Runs independently
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
from services.generator import TelemetryGeneratorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global generator instance
generator = None
generator_thread = None


def run_generator_loop():
    """Background thread running generator loop"""
    global generator
    
    try:
        round_num = 0
        while True:
            round_num += 1
            metrics = generator.generate_and_publish()
            
            logger.info(f"[{round_num:04d}] 📤 Published to Pub/Sub")
            logger.info(f"  Server:    {metrics['server']['server_id']} - CPU: {metrics['server']['cpu_percent']}%")
            logger.info(f"  Container: {metrics['container']['container_id']} - Req/s: {metrics['container']['requests_per_sec']}")
            logger.info(f"  Service:   {metrics['service']['service_name']} - Error: {metrics['service']['error_rate_percent']}%")
            
            time.sleep(300)
    
    except KeyboardInterrupt:
        logger.info("Generator loop interrupted")
    except Exception as e:
        logger.error(f"Generator error: {e}")


def create_app():
    """Create Flask app for Cloud Run"""
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'generator',
            'total_generated': generator.get_stats()['total_generated'] if generator else 0
        }), 200
    
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'service': 'Industrial Cloud Generator',
            'status': 'running',
            'description': 'Generates synthetic telemetry data and publishes to Pub/Sub'
        }), 200
    
    return app


def main():
    """Run Generator Service independently"""
    global generator, generator_thread
    
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
    
    # Initialize generator service
    pubsub = GCPPubSubBroker(project_id)
    generator = TelemetryGeneratorService(pubsub)
    
    logger.info("✅ Generator service ready")
    logger.info("📤 Publishing metrics every 5 minutes (conserving database space)")
    logger.info("Press Ctrl+C to stop\n")
    
    # Start generator loop in background thread
    generator_thread = threading.Thread(target=run_generator_loop, daemon=True)
    generator_thread.start()
    
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
        logger.info("🛑 Generator service stopped")
        if generator:
            stats = generator.get_stats()
            logger.info(f"📊 Total metrics generated: {stats['total_generated']}")
        logger.info("=" * 70)
