import threading
import logging
from connection_manager import RabbitMQConnectionManager

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self, connection_manager: RabbitMQConnectionManager,callback, exchange, routing_keys: list[str], queue_name=""):
        self.connection_manager = connection_manager
        self.callback = callback
        self.exchange = exchange
        self.routing_keys = routing_keys
        self.queue_name = queue_name
        self.channel = None

    def consume(self):
        self.channel = self.connection_manager.get_channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic', durable=True)
        result = self.channel.queue_declare(queue=self.queue_name, exclusive=True)
        queue_name = result.method.queue
        for routing_key in self.routing_keys:
            self.channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()
    
    def start_consuming(self):
        logger.info(f"Starting consumer thread for exchange:{self.exchange}")
        thread = threading.Thread(target=self.consume, daemon=True)
        thread.start()


