package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/aleksa-hubgit/user-service/data"
	"github.com/aleksa-hubgit/user-service/rabbitmq"
	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5"
	amqp "github.com/rabbitmq/amqp091-go"
)


var (
	username = os.Getenv("DATABASE_USERNAME")
	password = os.Getenv("DATABASE_PASSWORD")
	hostname = os.Getenv("DATABASE_HOSTNAME")
	port = os.Getenv("DATABASE_PORT")
	name = os.Getenv("DATABASE_NAME")
	connStr = fmt.Sprintf("postgresql://%s:%s@%s:%s/%s", username, password, hostname, port, name)
)
func main() {
	username := os.Getenv("DATABASE_USERNAME")
	password := os.Getenv("DATABASE_PASSWORD")
	hostname := os.Getenv("DATABASE_HOSTNAME")
	port := os.Getenv("DATABASE_PORT")
	name := os.Getenv("DATABASE_NAME")
	connStr := fmt.Sprintf("postgresql://%s:%s@%s:%s/%s", username, password, hostname, port, name)

	rabbitmqHostname := os.Getenv("RABBITMQ_HOSTNAME")
	rabbitmqPort, err := strconv.Atoi(os.Getenv("RABBITMQ_PORT"))
	if err != nil {
		log.Fatalf("could not convert RABBITMQ_PORT to int: %v", err)
	}
	rabbitmqUsername := os.Getenv("RABBITMQ_USERNAME")
	rabbitmqPassword := os.Getenv("RABBITMQ_PASSWORD")
	
	config := rabbitmq.NewRabbitMQConnectionConfig(rabbitmqHostname, rabbitmqPort, rabbitmqUsername, rabbitmqPassword, 5, 60)
	activityConnectionManager := rabbitmq.NewRabbitMQConnectionManager(config)
	reservationConnectionManager := rabbitmq.NewRabbitMQConnectionManager(config)
	userConnectionManager := rabbitmq.NewRabbitMQConnectionManager(config)
	subscriptionConnectionManager := rabbitmq.NewRabbitMQConnectionManager(config)
	defer activityConnectionManager.Close()
	defer reservationConnectionManager.Close()
	defer userConnectionManager.Close()
	defer subscriptionConnectionManager.Close()

	publisher := rabbitmq.NewRabbitMQPublisher(userConnectionManager, "user")

	activityConsumer := rabbitmq.NewRabbitMQConsumer(activityConnectionManager, activityCallback, "activity", []string{"created", "updated", "deleted", "cancelled"})
	reservationConsumer := rabbitmq.NewRabbitMQConsumer(reservationConnectionManager, reservationCallback, "reservation", []string{"created", "updated", "deleted"})
	subscriptionConsumer := rabbitmq.NewRabbitMQConsumer(subscriptionConnectionManager, subscriptionCallback, "subscription", []string{"created", "canceled"})
	go activityConsumer.StartConsuming()
	go reservationConsumer.StartConsuming()
	go subscriptionConsumer.StartConsuming()

	// connStr := "postgresql://token:token@localhost:5432/token"
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())
	service := NewUserService(database, publisher)
	handler := NewUserHandler(service)
	r := gin.Default()
	group := r.Group("/users")
	{
		group.GET("/:emailOrUsername", handler.GetUserByEmailOrUsername)
		group.GET("/", handler.ListUsers)
		group.PUT("/", handler.UpdateUser)
		group.POST("/", handler.CreateUser)
		group.DELETE("/", handler.DeleteUser)
	}
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("could not run server: %v", err)
	}

}

func saveActivityToDatabase(ctx context.Context, activity data.Activity) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	ac, err := database.CreateActivity(ctx, data.CreateActivityParams(activity))
	if err != nil {
		log.Printf("Failed to save activity to database: %v", err)
		return err
	}
	log.Printf("Activity %s added to the database", ac.Name)
	return nil
}

func saveReservationToDatabase(ctx context.Context, reservation data.Reservation) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	ac, err := database.CreateReservation(ctx, data.CreateReservationParams(reservation))
	if err != nil {
		log.Printf("Failed to save reservation to database: %v", err)
		return err
	}
	log.Printf("Reservation %d added to the database", ac.ID)
	return nil
}

func activityCallback(d amqp.Delivery) {
	log.Println("Message received:", string(d.Body))
	log.Println("Routing key:", string(d.RoutingKey))
	ctx := context.Background()
	
	activity, err := parseActivityMessage(d.Body)
	if err != nil {
		log.Printf("Failed to parse user message: %v", err)
		return
	}
	err = saveActivityToDatabase(ctx, activity)
	if err != nil {
		log.Printf("Failed to save activity to database: %v", err)
		return
	}
	log.Printf("Activity %s added to the database", activity.Name)
}

func reservationCallback(d amqp.Delivery) {
	log.Println("Message received:", string(d.Body))
	log.Println("Routing key:", string(d.RoutingKey))
	ctx := context.Background()
	reservation, err := parseReservationMessage(d.Body)
	if err != nil {
		log.Printf("Failed to parse reservation message: %v", err)
		return
	}
	err = saveReservationToDatabase(ctx, reservation)
	if err != nil {
		log.Printf("Failed to save reservation to database: %v", err)
		return
	}
	log.Printf("Reservation %d added to the database", reservation.ID)
}

func parseActivityMessage(body []byte) (data.Activity, error) {
	var activity data.Activity
	err := json.Unmarshal(body, &activity)
	if err != nil {
		return activity, err
	}
	return activity, nil
}

func parseReservationMessage(body []byte) (data.Reservation, error) {
	var reservation data.Reservation
	err := json.Unmarshal(body, &reservation)
	if err != nil {
		return reservation, err
	}
	return reservation, nil
}

func subscriptionCallback(d amqp.Delivery) {
	log.Println("Message received:", string(d.Body))
	log.Println("Routing key:", string(d.RoutingKey))
	ctx := context.Background()
	subscription, err := parseSubscriptionMessage(d.Body)
	if err != nil {
		log.Printf("Failed to parse subscription message: %v", err)
		return
	}
	err = saveSubscriptionToDatabase(ctx, subscription)
	if err != nil {
		log.Printf("Failed to save subscription to database: %v", err)
		return
	}
	log.Printf("Subscription %d added to the database", subscription.ID)
}

func parseSubscriptionMessage(body []byte) (data.Subscription, error) {
	var subscription data.Subscription
	err := json.Unmarshal(body, &subscription)
	if err != nil {
		return subscription, err
	}
	return subscription, nil
}

func saveSubscriptionToDatabase(ctx context.Context, subscription data.Subscription) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	ac, err := database.CreateSubscription(ctx, data.CreateSubscriptionParams(subscription))
	if err != nil {
		log.Printf("Failed to save subscription to database: %v", err)
		return err
	}
	log.Printf("Subscription %d added to the database", ac.ID)
	return nil
}

