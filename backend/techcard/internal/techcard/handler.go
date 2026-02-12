package techcard

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"strings"
	"techcard/db"
	internal_db "techcard/internal/db"

	"github.com/gin-gonic/gin"
)

type Handler struct {
	db *db.PrismaClient
}

func NewHandler() *Handler {
	return &Handler{
		db: internal_db.GetClient(),
	}
}

// GetTechCards возвращает список техкарт
func (h *Handler) GetTechCards(c *gin.Context) {
	techcards, err := h.db.TechCard.FindMany().Exec(context.Background())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch techcards"})
		return
	}
	c.JSON(http.StatusOK, techcards)
}

// CreateTechCard создает новую техкарту
func (h *Handler) CreateTechCard(c *gin.Context) {
	var req TechCardUpdate
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Создаем новую техкарту
	created, err := h.db.TechCard.CreateOne(
		db.TechCard.Tema.Set(req.Tema),
		db.TechCard.ID.Set(req.ID), // Если ID передается, иначе уберите эту строку
	).Exec(context.Background())

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create techcard: " + err.Error()})
		return
	}

	c.JSON(http.StatusCreated, created)
}



// UpdateTechCard обновляет или создает техкарту
func (h *Handler) UpdateTechCard(c *gin.Context) {
	techcardID := c.Param("techcard_id")
	var req TechCardUpdate
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	id := 0
	fmt.Sscanf(techcardID, "%d", &id)

	// В Go Prisma UpdateOne с Upsert логикой или просто Find + Create/Update
	// Для простоты имитируем Python логику: пытаемся найти, если нет - создаем
	_, err := h.db.TechCard.FindUnique(
		db.TechCard.ID.Equals(id),
	).Exec(context.Background())

	if err != nil {
		// Создаем новую с обязательными полями (Tema первая)
		_, _ = h.db.TechCard.CreateOne(
			db.TechCard.Tema.Set(""),
			db.TechCard.ID.Set(id),
		).Exec(context.Background())
	}

	// Обновляем основные поля
	_, err = h.db.TechCard.FindUnique(db.TechCard.ID.Equals(id)).Update(
		db.TechCard.GroupID.Set(req.GroupID),
		db.TechCard.LessonID.Set(req.LessonID),
		db.TechCard.LessonTypeID.Set(req.LessonTypeID),
		db.TechCard.NomerZanyatiya.Set(req.NomerZanyatiya),
		db.TechCard.PedTech.Set(req.PedTech),
		db.TechCard.CelZanyatiya.Set(req.CelZanyatiya),
		db.TechCard.ZadachiObuch.Set(req.ZadachiObuch),
		db.TechCard.ZadachiRazv.Set(req.ZadachiRazv),
		db.TechCard.ZadachiVosp.Set(req.ZadachiVosp),
		db.TechCard.PrognozResult.Set(req.PrognozResult),
		db.TechCard.Oborudovanie.Set(req.Oborudovanie),
		db.TechCard.Istochniki.Set(req.Istochniki),
	).Exec(context.Background())

	// Удаляем старые этапы
	_, _ = h.db.TechCardStage.FindMany(
		db.TechCardStage.TechCardID.Equals(id),
	).Delete().Exec(context.Background())

	// Создаем новые этапы
	for _, s := range req.Stages {
		_, _ = h.db.TechCardStage.CreateOne(
			db.TechCardStage.NomerEtapa.Set(s.NomerEtapa),
			db.TechCardStage.NazvanieEtapa.Set(s.NazvanieEtapa),
			db.TechCardStage.TechCard.Link(db.TechCard.ID.Equals(id)),
			db.TechCardStage.CelEtapa.Set(s.CelEtapa),
			db.TechCardStage.Dlitelnost.Set(s.Dlitelnost),
			db.TechCardStage.DeyatelnostPrepod.Set(s.DeyatelnostPrepod),
			db.TechCardStage.DeyatelnostObuch.Set(s.DeyatelnostObuch),
			db.TechCardStage.FormiruemyeKompetencii.Set(s.FormiruemyeKompetencii),
		).Exec(context.Background())
	}

	c.JSON(http.StatusOK, gin.H{"status": "updated", "id": id})
}

// Download эндпоинт вызывающий Python воркер
func (h *Handler) Download(c *gin.Context) {
	techcardID := c.Query("id")
	if techcardID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	id := 0
	fmt.Sscanf(techcardID, "%d", &id)

	// 1. Получаем данные из БД
	card, err := h.db.TechCard.FindUnique(db.TechCard.ID.Equals(id)).With(
		db.TechCard.Stages.Fetch(),
	).Exec(context.Background())

	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Techcard not found"})
		return
	}

	groupID, _ := card.GroupID()
	// 2. Подготавливаем JSON для Python
	input := map[string]interface{}{
		"techcard": card,
		"stages":   card.Stages(),
		// Здесь можно добавить group_name и т.д., если они есть в связанных таблицах
		"group_name": "Группа " + fmt.Sprint(groupID),
	}

	inputJSON, _ := json.Marshal(input)

	// 3. Вызываем Python воркер
	// Используем путь к перемещенному воркеру
	cmd := exec.Command("python3", "_python_legacy/generator_wrapper.py")
	cmd.Stdin = strings.NewReader(string(inputJSON))

	output, err := cmd.CombinedOutput()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Generator failed",
			"details": string(output),
		})
		return
	}

	// 4. Читаем путь к файлу из вывода (последняя строка)
	lines := strings.Split(strings.TrimSpace(string(output)), "\n")
	filePath := lines[len(lines)-1]

	c.FileAttachment(filePath, "techcard.docx")
}
