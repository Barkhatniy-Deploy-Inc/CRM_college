package db

import (
	"log"
	"schedule/db"
	"sync"
)

var (
	client *db.PrismaClient
	once   sync.Once
)

// GetClient returns the singleton Prisma Client instance
func GetClient() *db.PrismaClient {
	once.Do(func() {
		client = db.NewClient()
		if err := client.Prisma.Connect(); err != nil {
			log.Fatalf("Failed to connect to database: %v", err)
		}
	})
	return client
}

// Disconnect closes the database connection
func Disconnect() {
	if client != nil {
		if err := client.Prisma.Disconnect(); err != nil {
			log.Printf("Failed to disconnect from database: %v", err)
		}
	}
}
