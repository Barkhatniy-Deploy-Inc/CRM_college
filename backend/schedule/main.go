package main

import (
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

	// Routes (Синхронизация с фронтендом)
	apiGroup := r.Group("/api/schedule")
	{
		apiGroup.POST("/upload", handler.UploadSchedule)
		// Здесь должны быть ручки для /groups, /lessons и т.д.
	}

	// Фронт иногда стучится без /api
	scheduleGroup := r.Group("/schedule")
	{
		scheduleGroup.GET("/lessons", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Schedule list endpoint"})
		})
	}

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	log.Println("Schedule Service starting on :8000")
	if err := r.Run(":8000"); err != nil {
		log.Fatal(err)
	}
}
