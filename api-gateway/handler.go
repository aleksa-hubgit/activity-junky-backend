package main

import (
	"io"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

// TODO: Ovo bi trebalo sve da radi na bazi gRPC-a, a ne HTTP-a jer je brze i efikasnije
// TODO: Izvuci jednu metodi od svih ovih handlera jer se ponavlja kod
func UserHandler(c *gin.Context) {
	userServiceURL := userServiceURL + c.Request.URL.Path

	// Create a new request to the user service
	req, err := http.NewRequest(c.Request.Method, userServiceURL, c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers from the original request
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Send the request to the user service
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send request"})
		return
	}
	defer resp.Body.Close()

	// Copy the response from the user service back to the original client
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read response"})
		return
	}

	for key, values := range resp.Header {
		for _, value := range values {
			c.Writer.Header().Add(key, value)
		}
	}
	c.Writer.WriteHeader(resp.StatusCode)
	c.Writer.Write(body)
}

func ActivityHandler(c *gin.Context) {
	activityServiceURL := activityServiceURL + c.Request.URL.Path

	if len(c.Request.URL.RawQuery) > 0 {
		activityServiceURL += "?" + c.Request.URL.RawQuery
	}

	// Create a new request to the activity service
	req, err := http.NewRequest(c.Request.Method, activityServiceURL, c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers from the original request
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Send the request to the activity service
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send request"})
		return
	}
	defer resp.Body.Close()

	// Copy the response from the activity service back to the original client
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read response"})
		return
	}

	for key, values := range resp.Header {
		for _, value := range values {
			c.Writer.Header().Add(key, value)
		}
	}
	c.Writer.WriteHeader(resp.StatusCode)
	c.Writer.Write(body)
}

func ReviewHandler(c *gin.Context) {
	reviewServiceURL := reviewServiceURL + c.Request.URL.Path

	// Create a new request to the review service
	// TODO: izvuci ovo u metodu da se ne ponavlja!!!
	req, err := http.NewRequest(c.Request.Method, reviewServiceURL, c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers from the original request
	// TODO: izvuci ovo u metodu da se ne ponavlja!!!
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Send the request to the review service
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send request"})
		return
	}
	defer resp.Body.Close()

	// Copy the response from the review service back to the original client
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read response"})
		return
	}
	// TODO: izvuci ovo u metodu da se ne ponavlja!!!
	for key, values := range resp.Header {
		for _, value := range values {
			c.Writer.Header().Add(key, value)
		}
	}
	c.Writer.WriteHeader(resp.StatusCode)
	c.Writer.Write(body)
}

func AuthHandler(c *gin.Context) {
	authServiceURL := authServiceURL + c.Request.URL.Path

	// Create a new request to the auth service
	req, err := http.NewRequest(c.Request.Method, authServiceURL, c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers from the original request
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Send the request to the auth service
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send request"})
		return
	}
	defer resp.Body.Close()

	// Copy the response from the auth service back to the original client
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read response"})
		return
	}

	for key, values := range resp.Header {
		for _, value := range values {
			c.Writer.Header().Add(key, value)
		}
	}
	c.Writer.WriteHeader(resp.StatusCode)
	c.Writer.Write(body)
}

func ProxyRequest(c *gin.Context, serviceURL string) {
    fullURL := serviceURL + c.Request.URL.Path
    if len(c.Request.URL.RawQuery) > 0 {
        fullURL += "?" + c.Request.URL.RawQuery
    }

    req, err := http.NewRequest(c.Request.Method, fullURL, c.Request.Body)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
        return
    }
	log.Println("Request URL: ", req.URL)
	log.Println("Request Method: ", req.Method)
	log.Println("Request Body: ", req.Body)
	

    // Copy headers
    for key, values := range c.Request.Header {
        for _, value := range values {
            req.Header.Add(key, value)
        }
    }

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send request"})
        return
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read response"})
        return
    }

    // Copy response headers
    for key, values := range resp.Header {
        for _, value := range values {
            c.Writer.Header().Add(key, value)
        }
    }

    c.Writer.WriteHeader(resp.StatusCode)
    c.Writer.Write(body)
}
