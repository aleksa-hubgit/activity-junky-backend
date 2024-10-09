package main

import (
	"log"
	"os"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

var (
	userServiceURL = "http://user-service:8080"
	authServiceURL = "http://auth-service:8080"
	activityServiceURL = "http://activity-service:8080"
	reviewServiceURL = "http://review-service:8080"
)

func main() {
	userServiceURL = os.Getenv("USER_SERVICE_URL")
	authServiceURL = os.Getenv("AUTH_SERVICE_URL")
	activityServiceURL = os.Getenv("ACTIVITY_SERVICE_URL")
	reviewServiceURL = os.Getenv("REVIEW_SERVICE_URL")
	r := gin.Default()
	r.RedirectTrailingSlash = false
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000", "http://127.0.0.1:3000"}, 
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}, 
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},        
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,                                                      
	}))

	auth := r.Group("/auth")
	{
		auth.Any("", func(c *gin.Context) {
			ProxyRequest(c, authServiceURL)
		})
		auth.Any("/*action", func(c *gin.Context) {
			ProxyRequest(c, authServiceURL)
		})
	}
	users := r.Group("/users")
	users.Use(AuthMiddleware)
	{
		users.Any("", func(c *gin.Context) {
			ProxyRequest(c, userServiceURL)
		})
		users.Any("/*action", func(c *gin.Context) {
			ProxyRequest(c, userServiceURL)
		})  
	}

	
	activities := r.Group("/activities")
	activities.GET("", func(c *gin.Context) {
		ProxyRequest(c, activityServiceURL)
	})
	activities.Use(AuthMiddleware)
	{
		activities.Any("/*action", func(c *gin.Context) {
			ProxyRequest(c, activityServiceURL)
		})
	}

	reviews := r.Group("/reviews")
	reviews.Use(AuthMiddleware)
	{
		reviews.Any("", func(c *gin.Context) {
			ProxyRequest(c, reviewServiceURL)
		})
		reviews.Any("/*action", func(c *gin.Context) {
			ProxyRequest(c, reviewServiceURL)
		})
	}
	

	if err := r.Run(":8080"); err != nil {
		log.Fatalf("could not run server: %v", err)
	}
}