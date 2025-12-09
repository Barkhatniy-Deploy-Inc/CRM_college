#!/bin/bash

# Примеры API запросов для тестирования CRM_college
# Использование: ./scripts/api_examples.sh

echo "🔌 Примеры API запросов для CRM_college"
echo "======================================="

# Базовые URL сервисов
AUTH_URL="http://localhost:8002"
SCHEDULE_URL="http://localhost:8000"
TECHCARD_URL="http://localhost:8001"

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${BLUE}📊 Health Check endpoints:${NC}"
echo "curl $AUTH_URL/api/health"
echo "curl $SCHEDULE_URL/api/health"
echo "curl $TECHCARD_URL/api/health"

echo -e "\n${BLUE}🔐 Auth Service:${NC}"

echo -e "\n${GREEN}Регистрация пользователя:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
EOF

echo -e "\n${GREEN}Вход в систему:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
EOF

echo -e "\n${GREEN}Получение профиля (требует токен):${NC}"
cat << 'EOF'
# Сначала получите токен из login запроса
TOKEN="your-jwt-token-here"

curl -X GET http://localhost:8002/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
EOF

echo -e "\n${GREEN}Валидация токена:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8002/api/auth/validate \
  -H "Authorization: Bearer $TOKEN"
EOF

echo -e "\n${GREEN}Выход из системы:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8002/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
EOF

echo -e "\n${BLUE}📅 Schedule Service:${NC}"

echo -e "\n${GREEN}Получение всех курсов:${NC}"
echo "curl -X GET $SCHEDULE_URL/api/courses"

echo -e "\n${GREEN}Поиск курсов по названию:${NC}"
echo "curl -X GET '$SCHEDULE_URL/api/courses?name=Python&limit=5'"

echo -e "\n${GREEN}Создание курса (требует авторизации):${NC}"
cat << 'EOF'
curl -X POST http://localhost:8000/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Основы Python",
    "description": "Изучение основ программирования на Python",
    "duration_hours": 40
  }'
EOF

echo -e "\n${GREEN}Получение курса по ID:${NC}"
echo "curl -X GET $SCHEDULE_URL/api/courses/1"

echo -e "\n${GREEN}Обновление курса:${NC}"
cat << 'EOF'
curl -X PUT http://localhost:8000/api/courses/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Продвинутый Python",
    "description": "Углубленное изучение Python"
  }'
EOF

echo -e "\n${GREEN}Получение расписания:${NC}"
echo "curl -X GET $SCHEDULE_URL/api/schedule"

echo -e "\n${GREEN}Получение расписания за определенную дату:${NC}"
echo "curl -X GET '$SCHEDULE_URL/api/schedule?date=2024-01-15'"

echo -e "\n${GREEN}Получение расписания за период:${NC}"
echo "curl -X GET '$SCHEDULE_URL/api/schedule?date_from=2024-01-01&date_to=2024-01-31'"

echo -e "\n${GREEN}Создание урока в расписании:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "course_id": 1,
    "auditorium_id": 1,
    "teacher_id": 1,
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:30:00",
    "topic": "Введение в Python"
  }'
EOF

echo -e "\n${GREEN}Получение аудиторий:${NC}"
echo "curl -X GET $SCHEDULE_URL/api/auditoriums"

echo -e "\n${GREEN}Создание аудитории:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8000/api/auditoriums \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Аудитория 101",
    "capacity": 30,
    "equipment": ["проектор", "компьютер", "доска"]
  }'
EOF

echo -e "\n${GREEN}Участники курса:${NC}"
echo "curl -X GET $SCHEDULE_URL/api/courses/1/participants"

echo -e "\n${GREEN}Добавление участника к курсу:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8000/api/courses/1/participants \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "user_id": 2
  }'
EOF

echo -e "\n${GREEN}Получение календаря пользователя:${NC}"
cat << 'EOF'
curl -X GET http://localhost:8000/api/calendar/me.ics \
  -H "Authorization: Bearer $TOKEN" \
  -o my_schedule.ics
EOF

echo -e "\n${BLUE}📋 Techcard Service:${NC}"

echo -e "\n${GREEN}Корневой endpoint:${NC}"
echo "curl -X GET $TECHCARD_URL/"

echo -e "\n${GREEN}Получение техкарт (если endpoint существует):${NC}"
echo "curl -X GET $TECHCARD_URL/api/techcards"

echo -e "\n${GREEN}Создание техкарты:${NC}"
cat << 'EOF'
curl -X POST http://localhost:8001/api/techcards \
  -H "Content-Type: application/json" \
  -d '{
    "tema": "Основы алгоритмов",
    "group_id": 1,
    "lesson_id": 1,
    "teacher_id": 1,
    "content": "Изучение базовых алгоритмов сортировки"
  }'
EOF

echo -e "\n${BLUE}🔌 WebSocket подключение:${NC}"

echo -e "\n${GREEN}Подключение к WebSocket (Schedule Service):${NC}"
cat << 'EOF'
# Используйте wscat или другой WebSocket клиент
wscat -c ws://localhost:8000/ws

# Или с помощью JavaScript в браузере:
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = function(event) {
    console.log('Получено:', JSON.parse(event.data));
};
EOF

echo -e "\n${BLUE}🧪 Тестовые сценарии:${NC}"

echo -e "\n${YELLOW}Полный сценарий тестирования:${NC}"
cat << 'EOF'
# 1. Проверяем health endpoints
curl http://localhost:8002/api/health
curl http://localhost:8000/api/health
curl http://localhost:8001/api/health

# 2. Регистрируем пользователя
curl -X POST http://localhost:8002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# 3. Логинимся и получаем токен
TOKEN=$(curl -s -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 4. Создаем курс
curl -X POST http://localhost:8000/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test Course","description":"Test Description"}'

# 5. Получаем список курсов
curl http://localhost:8000/api/courses
EOF

echo -e "\n${YELLOW}Для автоматического тестирования используйте:${NC}"
echo "python3 scripts/test_services.py"
echo "./scripts/quick_test.sh"

echo -e "\n======================================="
echo -e "💡 ${BLUE}Полезные советы:${NC}"
echo "• Сохраните токен из login запроса для авторизованных запросов"
echo "• Используйте jq для красивого форматирования JSON: curl ... | jq"
echo "• Проверяйте HTTP статус коды: curl -w '%{http_code}' ..."
echo "• Для отладки добавляйте -v флаг к curl командам"