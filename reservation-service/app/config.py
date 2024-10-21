class RabbitMQConnectionConfig:
    def __init__(self, hostname, port, username, password, retries=5, heartbeat=60):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.retries = retries
        self.heartbeat = heartbeat