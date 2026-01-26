package main

import (
	"auth/internal/auth"
	"auth/internal/db"
	internalMiddleware "auth/internal/middleware"
	"common/middleware"
	"log"
	"net/http"

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

	// Auth routes (Убрали /api, так как фронт шлет сразу /auth/login)
	h := auth.NewHandler()
	authGroup := r.Group("/auth")
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

	log.Println("Auth Service starting on :8000")
	if err := r.Run(":8000"); err != nil {
		log.Fatal(err)
	}
}
