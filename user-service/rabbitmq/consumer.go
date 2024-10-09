package rabbitmq

import (
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitMQConsumer struct {
	connectionManager *RabbitMQConnectionManager
	callback          func(amqp.Delivery)
	exchange          string
	routingKeys	   []string
	channel           *amqp.Channel
}

// NewRabbitMQConsumer creates a new RabbitMQConsumer instance
func NewRabbitMQConsumer(connectionManager *RabbitMQConnectionManager, callback func(amqp.Delivery), exchange string, routingKeys []string) *RabbitMQConsumer {
	return &RabbitMQConsumer{
		connectionManager: connectionManager,
		callback:          callback,
		exchange:          exchange,
		routingKeys:       routingKeys,
	}
}

// Consume establishes the channel, declares the exchange, binds the queue, and starts consuming messages
func (r *RabbitMQConsumer) Consume() {
	var err error
	r.channel = r.connectionManager.GetChannel()

	// Declare exchange
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
		log.Fatalf("Failed to declare exchange: %v", err)
	}

	// Declare exclusive queue
	queue, err := r.channel.QueueDeclare(
		"",    // name (empty for exclusive, generated name)
		false, // durable
		false, // delete when unused
		true,  // exclusive
		false, // no-wait
		nil,   // arguments
	)
	if err != nil {
		log.Fatalf("Failed to declare queue: %v", err)
	}

	for _, routingKey := range r.routingKeys {
		err = r.channel.QueueBind(
			queue.Name,   // queue name
			routingKey,   // routing key
			r.exchange,   // exchange name
			false,        // no-wait
			nil,          // arguments
		)
		if err != nil {
			log.Fatalf("Failed to bind queue: %v", err)
		}
	}
	
	if err != nil {
		log.Fatalf("Failed to bind queue: %v", err)
	}

	// Start consuming messages
	msgs, err := r.channel.Consume(
		queue.Name, // queue name
		"",         // consumer tag
		true,       // auto-ack
		false,      // exclusive
		false,      // no-local
		false,      // no-wait
		nil,        // args
	)
	if err != nil {
		log.Fatalf("Failed to start consuming messages: %v", err)
	}

	// Handle incoming messages
	for msg := range msgs {
		r.callback(msg)
	}
}

// StartConsuming starts the consumer in a separate goroutine
func (r *RabbitMQConsumer) StartConsuming() {
	log.Printf("Starting consumer for exchange: %s", r.exchange)
	go r.Consume() // Run Consume in a separate goroutine
}