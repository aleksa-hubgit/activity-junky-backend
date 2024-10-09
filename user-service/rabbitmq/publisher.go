package rabbitmq

import (
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitMQPublisher struct {
	connectionManager *RabbitMQConnectionManager
	exchange          string
	routingKey 	  string
	channel           *amqp.Channel
}

// NewRabbitMQPublisher creates a new RabbitMQPublisher instance
func NewRabbitMQPublisher(connectionManager *RabbitMQConnectionManager, exchange string) *RabbitMQPublisher {
	return &RabbitMQPublisher{
		connectionManager: connectionManager,
		exchange:          exchange,
	}
}

// Publish sends a message to the exchange. It ensures the channel is open and publishes the message.
func (r *RabbitMQPublisher) Publish(message []byte, routingKey string) error {
	var err error
	if r.channel == nil || r.channel.IsClosed() {
		r.channel = r.connectionManager.GetChannel()
	}

	// Declare the exchange
	err = r.channel.ExchangeDeclare(
		r.exchange,   // exchange name
		"topic",     // exchange type
		true,         // durable
		false,        // auto-deleted
		false,        // internal
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		log.Printf("Failed to declare exchange: %v", err)
		return err
	}

	// Publish the message
	err = r.channel.Publish(
		r.exchange, // exchange
		routingKey,         // routing key (empty for fanout)
		false,      // mandatory
		false,      // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        message,
			DeliveryMode: amqp.Persistent,
		},
	)
	if err != nil {
		log.Printf("Failed to publish message: %v", err)
		// Attempt to reconnect and republish the message
		r.channel = r.connectionManager.GetChannel()
		return r.Publish(message, routingKey) // Retry publishing
	}

	log.Printf(" [x] Sent message: %s", string(message))
	return nil
}