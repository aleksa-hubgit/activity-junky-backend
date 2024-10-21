package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Handler interface {
	GetUserByEmailOrUsername(*gin.Context)
	ListUsers(*gin.Context)
	CreateUser(*gin.Context)
	UpdateUser(*gin.Context)
	DeleteUser(*gin.Context)
}

type UserHandler struct {
	service Service
}

func (u *UserHandler) CreateUser(c *gin.Context) {
	req := CreateRequest{}
	if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "message": "invalid request",
        })
        return
    }
	log.Printf("creating user: %v", req.UserType)
	log.Printf("creating user: %v", req.Username)
	log.Printf("creating user: %v", req.Email)
	user, err := u.service.CreateUser(c, req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": err.Error(),
		})
		return
	}
	c.JSON(http.StatusOK, user)
}

func (u *UserHandler) DeleteUser(c *gin.Context) {
	req := UserDeleteRequest{}
	if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "message": "invalid request",
        })
        return
    }
	err := u.service.DeleteUser(c, req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": err.Error(),
		})
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"message": fmt.Sprintf("deleted user: %s", req.Username),
	})
}

func (u *UserHandler) GetUserByEmailOrUsername(c *gin.Context) {
	emailOrUsername := c.Param("emailOrUsername")
	if emailOrUsername == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"message": "invalid request",
		})
		return 
	}
	user, err := u.service.GetUserByEmailOrUsername(c, emailOrUsername)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": "internal server error",
			"error": err.Error(),
		})
		return
	}
	c.JSON(http.StatusOK, user)
}

func (u *UserHandler) ListUsers(c *gin.Context) {
	users, err := u.service.ListUsers(c)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": "internal server error",
			"error": err.Error(),
		})
		return
	}
	c.JSON(http.StatusOK, users)
}

func (u *UserHandler) UpdateUser(c *gin.Context) {
	var req UserUpdateRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "message": "invalid request",
        })
        return
    }
	err := u.service.UpdateUser(c, req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": "internal server error",
			"error": err.Error(),
		})
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"message": fmt.Sprintf("updated user: %s", req.Username),
	})
}

func NewUserHandler(us Service) Handler {
	return &UserHandler{us}
}
