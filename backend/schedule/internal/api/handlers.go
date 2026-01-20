package api

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"schedule/internal/service"
	"time"

	"github.com/gin-gonic/gin"
)

type Handler struct {
	importer *service.ScheduleImporter
}

func NewHandler() *Handler {
	return &Handler{
		importer: service.NewScheduleImporter(),
	}
}

func (h *Handler) UploadSchedule(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File is required"})
		return
	}

	// Create temp dir if not exists
	tempDir := "temp_uploads"
	if _, err := os.Stat(tempDir); os.IsNotExist(err) {
		os.Mkdir(tempDir, 0755)
	}

	// Save file with unique name
	filename := fmt.Sprintf("%d_%s", time.Now().Unix(), file.Filename)
	filePath := filepath.Join(tempDir, filename)

	if err := c.SaveUploadedFile(file, filePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}
	defer os.Remove(filePath) // Clean up

	// Import
	stats := h.importer.ImportSchedule(filePath)

	if stats.Status == "error" {
		c.JSON(http.StatusBadRequest, stats)
		return
	}

	c.JSON(http.StatusOK, stats)
}
