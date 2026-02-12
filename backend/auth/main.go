package main

import (
	"auth/internal/auth"
	"auth/internal/db"
	internalMiddleware "auth/internal/middleware"
	"common/middleware"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	// Initialize DB
	db.GetClient()
	defer db.Disconnect()

	r := gin.Default()

	// CORS Middleware
	r.Use(middleware.CorsMiddleware())

	// Auth routes (Nginx strips /api/auth, so we listen on root /)
	h := auth.NewHandler()
	authGroup := r.Group("/")
	{
		authGroup.POST("/register", h.Register)
		authGroup.POST("/login", h.Login)

		// Protected routes
		protected := authGroup.Group("/")
		protected.Use(internalMiddleware.AuthMiddleware())
		{
			protected.GET("/me", h.Me)
		}
	}

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "service": "auth"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	log.Printf("Auth Service starting on :%s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatal(err)
	}
}
