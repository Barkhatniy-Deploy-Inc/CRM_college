package main

import (
	"common/middleware"
	"log"
	"os"
	"schedule/internal/api"
	"schedule/internal/db"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	if err := godotenv.Load(); err != nil {
		log.Printf("Error loading .env file: %v", err)
	} else {
		log.Println(".env file loaded successfully")
	}

	if os.Getenv("DATABASE_URL") == "" {
		log.Fatal("DATABASE_URL is not set in environment")
	} else {
		log.Println("DATABASE_URL is set")
	}

	// Initialize DB
	db.GetClient()
	defer db.Disconnect()

	// Initialize Handlers
	handler := api.NewHandler()

	r := gin.Default()

	// CORS Middleware
	r.Use(middleware.CorsMiddleware())

	// Routes (Синхронизация с фронтендом)
	// Routes (Nginx handles prefix stripping)
	apiGroup := r.Group("/")
	{
		apiGroup.POST("/upload", handler.UploadSchedule)
		apiGroup.GET("/lessons", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Schedule list endpoint"})
		})
	}


	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	log.Printf("Schedule Service starting on :%s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatal(err)
	}
}
