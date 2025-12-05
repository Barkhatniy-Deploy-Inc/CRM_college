# frontend/Dockerfile
# ========================================
# Этап 1: Сборка React приложения
# ========================================
FROM node:18-alpine AS builder

WORKDIR /app

# Копируем package файлы
COPY package*.json ./

# Ставим зависимости
RUN npm install

# Копируем исходники
COPY . .

# Собираем production билд
RUN npm run build

# ========================================
# Этап 2: Nginx для раздачи статики
# ========================================
FROM nginx:alpine AS production

# Удаляем дефолтный конфиг
RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш конфиг для статики
COPY nginx.conf /etc/nginx/conf.d/

# React кладёт билд в build/
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
