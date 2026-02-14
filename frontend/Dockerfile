# Этап 1: Сборка статики
FROM node:20-alpine AS build-stage

WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код
COPY . .

# Собираем проект
RUN npm run build

# Этап 2: Раздача через Nginx
FROM nginx:stable-alpine AS production-stage

# Копируем собранную статику из первого этапа
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Копируем кастомный конфиг Nginx (если он есть)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
