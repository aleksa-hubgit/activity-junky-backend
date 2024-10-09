package rabbitmq

type RabbitMQConnectionConfig struct {
	Hostname  string
	Port      int
	Username  string
	Password  string
	Retries   int
	Heartbeat int
}

// NewRabbitMQConnectionConfig is a constructor-like function to initialize the RabbitMQConnectionConfig
func NewRabbitMQConnectionConfig(hostname string, port int, username string, password string, retries int, heartbeat int) RabbitMQConnectionConfig {
	return RabbitMQConnectionConfig{
		Hostname:  hostname,
		Port:      port,
		Username:  username,
		Password:  password,
		Retries:   retries,
		Heartbeat: heartbeat,
	}
}