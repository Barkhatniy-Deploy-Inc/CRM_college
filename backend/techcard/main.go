package main

import (
	"log"
	"net/http"
	"techcard/internal/db"
	"techcard/internal/techcard"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	// Initialize DB
	db.GetClient()
	defer db.Disconnect()

	r := gin.Default()

	// CORS Middleware
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	h := techcard.NewHandler()

	api := r.Group("/api/techcards")
	{
		api.PUT("/:techcard_id", h.UpdateTechCard)
		api.GET("/download", h.Download)
	}

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "service": "techcard"})
	})

	log.Println("Techcard Service starting on :8000")
	if err := r.Run(":8000"); err != nil {
		log.Fatal(err)
	}
}
