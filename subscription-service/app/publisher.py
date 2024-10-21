import logging
import pika
from connection_manager import RabbitMQConnectionManager

logger = logging.getLogger(__name__)

class RabbitMQPublisher:
    def __init__(self, connection_manager: RabbitMQConnectionManager, exchange):
        self.connection_manager = connection_manager
        self.exchange = exchange
        self.channel = None
    
    def publish(self, message, routing_key):
        try:
            # Ensure channel is open
            if self.channel is None or self.channel.is_closed:
                self.channel = self.connection_manager.get_channel()
            
            # Declare the exchange
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic', durable=True)
            
            # Publish the message
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            logger.info(f" [x] Sent message: {message}")
        
        except pika.exceptions.AMQPError as e:
            logger.error(f"Failed to publish message due to AMQP error: {e}")
            # Try reconnecting and republishing the message
            self.channel = self.connection_manager.get_channel()
            self.publish(message, routing_key)