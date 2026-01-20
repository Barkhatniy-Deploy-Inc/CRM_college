package auth

import (
	"auth/db"
	internal_db "auth/internal/db"
	"auth/pkg/jwt"
	"auth/pkg/utils/security"
	"context"
	"net/http"
	"time"

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

// Register эндпоинт для регистрации нового пользователя
func (h *Handler) Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	hashedPassword, err := security.HashPassword(req.Password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	user, err := h.db.User.CreateOne(
		db.User.Email.Set(req.Email),
		db.User.PasswordHash.Set(hashedPassword),
		db.User.FullName.Set(req.FullName),
		db.User.Role.Set(db.UserRoleStudent),
	).Exec(context.Background())

	if err != nil {
		c.JSON(http.StatusConflict, gin.H{"error": "User already exists"})
		return
	}

	accessToken, refreshToken, err := jwt.GenerateTokenPair(user.ID, user.Email, string(user.Role))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate tokens"})
		return
	}

	// Сохраняем refresh токен в базу
	_, _ = h.db.RefreshToken.CreateOne(
		db.RefreshToken.Token.Set(refreshToken),
		db.RefreshToken.ExpiresAt.Set(time.Now().Add(7*24*time.Hour)),
		db.RefreshToken.User.Link(db.User.ID.Equals(user.ID)),
	).Exec(context.Background())

	c.JSON(http.StatusCreated, TokenResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresIn:    900, // 15 min
		User: UserResponse{
			ID:       user.ID,
			Email:    user.Email,
			FullName: user.FullName,
			Role:     string(user.Role),
			IsActive: user.IsActive,
		},
	})
}

// Login эндпоинт для входа в систему
func (h *Handler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := h.db.User.FindUnique(
		db.User.Email.Equals(req.Email),
	).Exec(context.Background())

	if err != nil || !security.VerifyPassword(req.Password, user.PasswordHash) {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid email or password"})
		return
	}

	accessToken, refreshToken, err := jwt.GenerateTokenPair(user.ID, user.Email, string(user.Role))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate tokens"})
		return
	}

	c.JSON(http.StatusOK, TokenResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresIn:    900,
		User: UserResponse{
			ID:       user.ID,
			Email:    user.Email,
			FullName: user.FullName,
			Role:     string(user.Role),
			IsActive: user.IsActive,
		},
	})
}

// Me эндпоинт для получения данных текущего пользователя
func (h *Handler) Me(c *gin.Context) {
	userID, _ := c.Get("userID")

	user, err := h.db.User.FindUnique(
		db.User.ID.Equals(userID.(int)),
	).Exec(context.Background())

	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, UserResponse{
		ID:       user.ID,
		Email:    user.Email,
		FullName: user.FullName,
		Role:     string(user.Role),
		IsActive: user.IsActive,
	})
}
