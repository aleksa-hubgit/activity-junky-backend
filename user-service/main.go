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

func saveActivity(ctx context.Context, activity data.Activity) error {
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

func saveReservation(ctx context.Context, reservation data.Reservation) error {
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

func deleteActivity(ctx context.Context, activity data.Activity) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	err = database.DeleteActivity(ctx, activity.ID)
	if err != nil {
		log.Printf("Failed to delete activity from database: %v", err)
		return err
	}
	log.Printf("Activity %s deleted from the database", activity.Name)
	return nil
}

func updateActivity(ctx context.Context, activity data.Activity) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	err = database.UpdateActivity(ctx, data.UpdateActivityParams(activity))
	if err != nil {
		log.Printf("Failed to update activity in the database: %v", err)
		return err
	}
	log.Printf("Activity %s updated in the database", activity.Name)
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
	if d.RoutingKey == "deleted" {
		log.Printf("Activity %s deleted", string(d.Body))
		err = deleteActivity(ctx, activity)
		if err != nil {
			log.Printf("Failed to delete activity from database: %v", err)
		}
		return
	} else if d.RoutingKey == "updated" {
		log.Printf("Activity %s updated", string(d.Body))
		err = updateActivity(ctx, activity)
		if err != nil {
			log.Printf("Failed to update activity in the database: %v", err)
		}
		return
	} else if d.RoutingKey == "created" {
		log.Printf("Activity %s created", string(d.Body))
		err = saveActivity(ctx, activity)
		if err != nil {
			log.Printf("Failed to save activity to database: %v", err)
		}
		return
	}
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
	if d.RoutingKey == "deleted" {
		log.Printf("Reservation %d deleted", reservation.ID)
		err = deleteReservation(ctx, reservation)
		if err != nil {
			log.Printf("Failed to delete reservation from database: %v", err)
		}
		return
	} else if d.RoutingKey == "updated" {
		log.Printf("Reservation %d updated", reservation.ID)
		err = updateReservation(ctx, reservation)
		if err != nil {
			log.Printf("Failed to update reservation in the database: %v", err)
		}
		return
	} else if d.RoutingKey == "created" {
		log.Printf("Reservation %d created", reservation.ID)
		err = saveReservation(ctx, reservation)
		if err != nil {
			log.Printf("Failed to save reservation to database: %v", err)
		}
		return
	}
}

func deleteReservation(ctx context.Context, reservation data.Reservation) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	err = database.DeleteReservation(ctx, reservation.ID)
	if err != nil {
		log.Printf("Failed to delete reservation from database: %v", err)
		return err
	}
	log.Printf("Reservation %d deleted from the database", reservation.ID)
	return nil
}

func updateReservation(ctx context.Context, reservation data.Reservation) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	err = database.UpdateReservation(ctx, data.UpdateReservationParams(reservation))
	if err != nil {
		log.Printf("Failed to update reservation in the database: %v", err)
		return err
	}
	log.Printf("Reservation %d updated in the database", reservation.ID)
	return nil
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
	if d.RoutingKey == "deleted" {
		log.Printf("Subscription %d canceled", subscription.ID)
		err = deleteSubscription(ctx, subscription)
		if err != nil {
			log.Printf("Failed to cancel subscription: %v", err)
		}
		return
	} else if d.RoutingKey == "created" {
		log.Printf("Subscription %d created", subscription.ID)
		err = saveSubscription(ctx, subscription)
		if err != nil {
			log.Printf("Failed to save subscription to database: %v", err)
		}
	}
}

func parseSubscriptionMessage(body []byte) (data.Subscription, error) {
	var subscription data.Subscription
	err := json.Unmarshal(body, &subscription)
	if err != nil {
		return subscription, err
	}
	return subscription, nil
}

func deleteSubscription(ctx context.Context, subscription data.Subscription) error {
	conn, err := pgx.Connect(context.Background(), connStr)
	if err != nil {
		log.Fatal(err)
	}
	database := data.New(conn)
	defer conn.Close(context.Background())

	err = database.DeleteSubscription(ctx, subscription.ID)
	if err != nil {
		log.Printf("Failed to cancel subscription: %v", err)
		return err
	}
	log.Printf("Subscription %d canceled", subscription.ID)
	return nil
}


func saveSubscription(ctx context.Context, subscription data.Subscription) error {
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

