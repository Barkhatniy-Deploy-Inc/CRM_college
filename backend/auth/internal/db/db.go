package db

import (
	"auth/db"
	"log"
	"sync"
)

var (
	client *db.PrismaClient
	once   sync.Once
)

// GetClient returns a singleton instance of the Prisma Client
func GetClient() *db.PrismaClient {
	once.Do(func() {
		client = db.NewClient()
		if err := client.Connect(); err != nil {
			log.Fatalf("Failed to connect to Prisma: %v", err)
		}
	})
	return client
}

// Disconnect closes the database connection
func Disconnect() {
	if client != nil {
		if err := client.Disconnect(); err != nil {
			log.Printf("Error disconnecting from Prisma: %v", err)
		}
	}
}
