"""
GCP Pub/Sub Broker
Cloud-native event streaming
"""

from google.cloud import pubsub_v1
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GCPPubSubBroker:
    """GCP Pub/Sub broker for event-driven streaming"""
    
    def __init__(self, project_id):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        
        # Topic names
        self.topic_names = {
            'server_metrics': 'server-metrics',
            'container_metrics': 'container-metrics',
            'service_metrics': 'service-metrics'
        }
        
        # Topic paths
        self.topics = {
            topic_id: f'projects/{project_id}/topics/{name}'
            for topic_id, name in self.topic_names.items()
        }
        
        logger.info(f"✅ Connected to GCP Project: {project_id}")
        self._ensure_topics_exist()
    
    def _ensure_topics_exist(self):
        """Create topics if they don't exist"""
        for topic_id, topic_path in self.topics.items():
            try:
                self.publisher.create_topic(request={'name': topic_path})
                logger.info(f"📌 Created topic: {self.topic_names[topic_id]}")
            except Exception as e:
                if 'ALREADY_EXISTS' in str(e):
                    logger.info(f"📌 Topic exists: {self.topic_names[topic_id]}")
                else:
                    logger.error(f"❌ Error creating topic: {e}")
    
    def publish(self, topic_id, message):
        """Publish message to topic"""
        topic_path = self.topics.get(topic_id)
        if not topic_path:
            logger.error(f"❌ Unknown topic: {topic_id}")
            return None
        
        try:
            message_json = json.dumps(message).encode('utf-8')
            future = self.publisher.publish(topic_path, message_json)
            message_id = future.result()
            return message_id
        except Exception as e:
            logger.error(f"❌ Failed to publish: {e}")
            return None
