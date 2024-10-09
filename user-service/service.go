package main

import (
	"context"
	"encoding/json"
	"errors"
	"log"

	"github.com/aleksa-hubgit/user-service/data"
	"github.com/aleksa-hubgit/user-service/rabbitmq"
)

type CreateRequest struct {
	Username string `json:"username"`
	Email    string `json:"email"`
	Password string `json:"password"`
	UserType data.UserType `json:"user_type"`
}
type UserUpdateRequest struct {
	Username string
	Email    string
}
type UserDeleteRequest struct {
	Username string
	Password string
}

type Service interface {
	GetUserByEmailOrUsername(context.Context, string) (*data.User, error)
	ListUsers(context.Context) ([]data.User, error)
	CreateUser(context.Context, CreateRequest) (*data.User, error)
	UpdateUser(context.Context, UserUpdateRequest) error
	DeleteUser(context.Context, UserDeleteRequest) error
}

type UserService struct {
	queries *data.Queries
	publisher *rabbitmq.RabbitMQPublisher
}

func (u *UserService) exists(ctx context.Context, username string) bool {
	_, err := u.queries.GetUserByUsername(ctx, username)
	return err == nil
}

// CreateUser implements Service.
func (u *UserService) CreateUser(ctx context.Context, rr CreateRequest) (*data.User, error) {
	if u.exists(ctx, rr.Username) {
		return nil, errors.New("user exists")
	}
	log.Printf("creating user: %v", rr.UserType)
	user, err := u.queries.CreateUser(ctx, data.CreateUserParams{Username: rr.Username, Email: rr.Email, Password: rr.Password, UserType: rr.UserType})
	if err != nil {
		return nil, err
	}
	body, err := json.Marshal(user)
	if err != nil {
		return nil, err
	}
	err = u.publisher.Publish(body, "created")
	if err != nil {
		return nil, err
	}
	return &user, nil
}


func (u *UserService) DeleteUser(ctx context.Context, udr UserDeleteRequest) error {
	toDelete, err := u.queries.GetUserByUsername(ctx, udr.Username)
	if err != nil {
		return err
	}
	if toDelete.Password != udr.Password {
		return errors.New("passwords don't match")
	}
	u.queries.DeleteUser(ctx, toDelete.ID)
	return nil
}

func (u *UserService) GetUserByEmailOrUsername(ctx context.Context, uname string) (*data.User, error) {
	user, err := u.queries.GetUserByEmailOrUsername(ctx, uname)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (u *UserService) ListUsers(ctx context.Context) ([]data.User, error) {
	users, err := u.queries.ListUsers(ctx)
	if err != nil {
		return nil, err
	}
	return users, nil
}

func (u *UserService) UpdateUser(ctx context.Context, uur UserUpdateRequest) error {
	toUpdate, err := u.queries.GetUserByUsername(ctx, uur.Username)
	if err != nil {
		return err
	}
	err = u.queries.UpdateUser(ctx, data.UpdateUserParams{Username: uur.Username, Email: uur.Email, Password: toUpdate.Password, ID: toUpdate.ID})
	if err != nil {
		return err
	}
	return nil
}

func NewUserService(queries *data.Queries, publisher *rabbitmq.RabbitMQPublisher) Service {
	return &UserService{queries: queries, publisher: publisher}
}
