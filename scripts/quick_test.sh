#!/bin/bash

# Быстрое тестирование сервисов CRM_college
# Использование: ./scripts/quick_test.sh

echo "🧪 Быстрое тестирование сервисов CRM_college"
echo "=============================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки сервиса
test_service() {
    local name=$1
    local url=$2
    local port=$3
    local health_path=$4
    
    echo -e "\n🔍 Тестирование $name ($url:$port)"
    
    # Проверяем доступность порта
    if ! nc -z localhost $port 2>/dev/null; then
        echo -e "  ❌ Порт $port недоступен"
        return 1
    fi
    
    # Проверяем health endpoint
    response=$(curl -s -w "%{http_code}" -o /tmp/health_response "$url:$port$health_path" 2>/dev/null)
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        echo -e "  ✅ Health check: ${GREEN}OK${NC} (HTTP $http_code)"
        
        # Показываем ответ
        if [ -f /tmp/health_response ]; then
            response_body=$(cat /tmp/health_response)
            echo "  📄 Response: $response_body"
        fi
        return 0
    else
        echo -e "  ❌ Health check: ${RED}FAIL${NC} (HTTP $http_code)"
        return 1
    fi
}

# Функция для тестирования API endpoints
test_api_endpoints() {
    echo -e "\n🔧 Тестирование API endpoints"
    
    # Тест Auth сервиса - регистрация
    echo -e "\n🔐 Auth Service - Регистрация:"
    timestamp=$(date +%s)
    register_data="{\"email\":\"test_$timestamp@example.com\",\"password\":\"testpass123\",\"full_name\":\"Test User\"}"
    
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$register_data" \
        -o /tmp/register_response \
        "http://localhost:8002/api/auth/register" 2>/dev/null)
    
    http_code="${response: -3}"
    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        echo -e "  ✅ Регистрация: ${GREEN}OK${NC} (HTTP $http_code)"
    else
        echo -e "  ❌ Регистрация: ${RED}FAIL${NC} (HTTP $http_code)"
    fi
    
    # Тест Schedule сервиса - получение групп
    echo -e "\n📅 Schedule Service - Группы:"
    response=$(curl -s -w "%{http_code}" -o /tmp/groups_response "http://localhost:8000/api/schedule/groups/" 2>/dev/null)
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        echo -e "  ✅ Получение групп: ${GREEN}OK${NC} (HTTP $http_code)"
    else
        echo -e "  ❌ Получение групп: ${RED}FAIL${NC} (HTTP $http_code)"
    fi
    
    # Тест Techcard сервиса
    echo -e "\n📋 Techcard Service - Root:"
    response=$(curl -s -w "%{http_code}" -o /tmp/techcard_response "http://localhost:8001/" 2>/dev/null)
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        echo -e "  ✅ Root endpoint: ${GREEN}OK${NC} (HTTP $http_code)"
    else
        echo -e "  ❌ Root endpoint: ${RED}FAIL${NC} (HTTP $http_code)"
    fi
}

# Функция для проверки Docker контейнеров
check_docker_containers() {
    echo -e "\n🐳 Проверка Docker контейнеров:"
    
    if command -v docker &> /dev/null; then
        # Проверяем запущенные контейнеры
        containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(auth|schedule|techcard)" || true)
        
        if [ -n "$containers" ]; then
            echo "$containers"
        else
            echo -e "  ⚠️ ${YELLOW}Docker контейнеры не найдены${NC}"
        fi
    else
        echo -e "  ⚠️ ${YELLOW}Docker не установлен${NC}"
    fi
}

# Функция для проверки зависимостей
check_dependencies() {
    echo -e "\n📦 Проверка зависимостей:"
    
    # Проверяем curl
    if command -v curl &> /dev/null; then
        echo -e "  ✅ curl: ${GREEN}установлен${NC}"
    else
        echo -e "  ❌ curl: ${RED}не установлен${NC}"
    fi
    
    # Проверяем netcat
    if command -v nc &> /dev/null; then
        echo -e "  ✅ netcat: ${GREEN}установлен${NC}"
    else
        echo -e "  ❌ netcat: ${RED}не установлен${NC}"
    fi
    
    # Проверяем Python
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version)
        echo -e "  ✅ Python: ${GREEN}$python_version${NC}"
    else
        echo -e "  ❌ Python: ${RED}не установлен${NC}"
    fi
}

# Основная функция
main() {
    # Проверяем зависимости
    check_dependencies
    
    # Проверяем Docker контейнеры
    check_docker_containers
    
    # Тестируем сервисы
    echo -e "\n📊 Тестирование сервисов:"
    
    services_ok=0
    total_services=3
    
    if test_service "Auth Service" "http://localhost" 8002 "/api/auth/health"; then
        ((services_ok++))
    fi
    
    if test_service "Schedule Service" "http://localhost" 8000 "/api/schedule/health"; then
        ((services_ok++))
    fi
    
    if test_service "Techcard Service" "http://localhost" 8001 "/api/techcard/health"; then
        ((services_ok++))
    fi
    
    # Тестируем API endpoints если сервисы работают
    if [ $services_ok -gt 0 ]; then
        test_api_endpoints
    fi
    
    # Итоговый отчет
    echo -e "\n=============================================="
    echo -e "📋 ИТОГОВЫЙ ОТЧЕТ:"
    echo -e "Работающих сервисов: $services_ok/$total_services"
    
    if [ $services_ok -eq $total_services ]; then
        echo -e "🎉 ${GREEN}Все сервисы работают корректно!${NC}"
        exit 0
    elif [ $services_ok -gt 0 ]; then
        echo -e "⚠️ ${YELLOW}Некоторые сервисы имеют проблемы${NC}"
        exit 1
    else
        echo -e "❌ ${RED}Сервисы не запущены${NC}"
        echo -e "\n💡 Для запуска сервисов используйте:"
        echo -e "   docker-compose up -d"
        echo -e "   или запустите сервисы локально"
        exit 2
    fi
}

# Очистка временных файлов при выходе
cleanup() {
    rm -f /tmp/health_response /tmp/register_response /tmp/groups_response /tmp/techcard_response
}
trap cleanup EXIT

# Запуск основной функции
main "$@"