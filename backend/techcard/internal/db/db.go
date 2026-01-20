package db

import (
	"log"
	"sync"
	"techcard/db"
)

var (
	client *db.PrismaClient
	once   sync.Once
)

func GetClient() *db.PrismaClient {
	once.Do(func() {
		client = db.NewClient()
		if err := client.Connect(); err != nil {
			log.Fatalf("Failed to connect to Prisma: %v", err)
		}
	})
	return client
}

func Disconnect() {
	if client != nil {
		if err := client.Disconnect(); err != nil {
			log.Printf("Error disconnecting from Prisma: %v", err)
		}
	}
}
