import time
import pika
from config import RabbitMQConnectionConfig
import logging

logger = logging.getLogger(__name__)


class RabbitMQConnectionManager:
    def __init__(self, config: RabbitMQConnectionConfig):
        self.config = config
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        self.connection = None
        retries = self.config.retries
        credentials = pika.PlainCredentials(self.config.username, self.config.password)
        parameters = pika.ConnectionParameters(host=self.config.hostname, 
                                               credentials=credentials,
                                               heartbeat=self.config.heartbeat)
        while self.connection is None and retries > 0:
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                logger.info(f"Connected to RabbitMQ at {self.config.hostname}")
            except Exception as e:
                logger.error(f"Error connecting to RabbitMQ: {e}")
                time.sleep(5)
                retries -= 1
        return self.connection

    def close(self):
        if self.connection is not None and self.connection.is_open:
            logger.info(f"Closing connection to RabbitMQ at {self.config.hostname}")
            self.connection.close()
    
    def get_channel(self):
        self._ensure_channel()
        return self.channel
    
    def _ensure_channel(self):
        self._ensure_connection()
        if self.channel is None or self.channel.is_closed:
            logger.info(f"Channel closed. Reopening channel to RabbitMQ at {self.config.hostname}")
            self.channel = self.connection.channel()
    
    def _ensure_connection(self):
        if self.connection is None or self.connection.is_closed:
            logger.info(f"Connection closed. Reconnecting to RabbitMQ at {self.config.hostname}")
            self.connect()