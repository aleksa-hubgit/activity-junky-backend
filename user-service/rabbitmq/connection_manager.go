package rabbitmq

import (
	"fmt"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitMQConnectionManager struct {
	config     RabbitMQConnectionConfig
	connection *amqp.Connection
	channel    *amqp.Channel
}

// NewRabbitMQConnectionManager creates a new RabbitMQConnectionManager instance
func NewRabbitMQConnectionManager(config RabbitMQConnectionConfig) *RabbitMQConnectionManager {
	manager := &RabbitMQConnectionManager{
		config: config,
	}
	manager.connect()
	return manager
}

// connect handles connecting to the RabbitMQ server and opening a channel
func (r *RabbitMQConnectionManager) connect() {
	var err error
	retries := r.config.Retries
	amqpURL := fmt.Sprintf("amqp://%s:%s@%s:%d/", r.config.Username, r.config.Password, r.config.Hostname, r.config.Port)

	for r.connection == nil && retries > 0 {
		r.connection, err = amqp.DialConfig(amqpURL, amqp.Config{
			Heartbeat: time.Duration(r.config.Heartbeat) * time.Second,
		})
		if err != nil {
			log.Printf("Error connecting to RabbitMQ: %v. Retrying...", err)
			time.Sleep(5 * time.Second)
			retries--
		} else {
			log.Printf("Connected to RabbitMQ at %s", r.config.Hostname)
			r.channel, err = r.connection.Channel()
			if err != nil {
				log.Fatalf("Failed to open a channel: %v", err)
			}
		}
	}

	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ after retries: %v", err)
	}
}

// Close handles closing the RabbitMQ connection
func (r *RabbitMQConnectionManager) Close() {
	if r.connection != nil && !r.connection.IsClosed() {
		log.Printf("Closing connection to RabbitMQ at %s", r.config.Hostname)
		err := r.connection.Close()
		if err != nil {
			log.Printf("Error closing RabbitMQ connection: %v", err)
		}
	}
}

// GetChannel ensures the connection is open and returns a channel
func (r *RabbitMQConnectionManager) GetChannel() *amqp.Channel {
	r.ensureChannel()
	return r.channel
}

// ensureChannel checks and reopens the channel if it is closed
func (r *RabbitMQConnectionManager) ensureChannel() {
	r.ensureConnection()
	if r.channel == nil || r.channel.IsClosed() {
		log.Printf("Channel closed. Reopening channel to RabbitMQ at %s", r.config.Hostname)
		var err error
		r.channel, err = r.connection.Channel()
		if err != nil {
			log.Fatalf("Failed to reopen RabbitMQ channel: %v", err)
		}
	}
}

// ensureConnection checks and reconnects if the connection is closed
func (r *RabbitMQConnectionManager) ensureConnection() {
	if r.connection == nil || r.connection.IsClosed() {
		log.Printf("Connection closed. Reconnecting to RabbitMQ at %s", r.config.Hostname)
		r.connect()
	}
}