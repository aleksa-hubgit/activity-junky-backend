package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func AuthMiddleware(c *gin.Context) {
	token := c.GetHeader("Authorization")

	verifyURL := authServiceURL + "/auth/verify"

	req, err := http.NewRequest("GET", verifyURL, nil)
	if err != nil {
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	req.Header.Set("Authorization", token)
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if resp.StatusCode != http.StatusOK {
		c.AbortWithStatusJSON(resp.StatusCode, gin.H{"error": "unauthorized"})
		return
	}
	c.Next()
}
