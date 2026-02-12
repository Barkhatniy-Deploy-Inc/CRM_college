package main

import (
	"common/middleware"
	"log"
	"net/http"
	"os"
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
	r.Use(middleware.CorsMiddleware())

	h := techcard.NewHandler()

	// Routes (Nginx handles prefix stripping)
	api := r.Group("/")
	{
		api.GET("/", h.GetTechCards) // Add list endpoint if missing or implies root
		api.POST("/", h.CreateTechCard)
		api.PUT("/:techcard_id", h.UpdateTechCard)
		api.GET("/download", h.Download)
	}

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "service": "techcard"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	log.Printf("Techcard Service starting on :%s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatal(err)
	}
}
