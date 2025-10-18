# --- Этап 1: Сборка Vue-приложения ---
FROM node:24-alpine as builder

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем весь остальной код фронтенда
COPY . .

# Собираем приложение для production. Результат будет в папке /app/dist/
RUN npm run build


# --- Этап 2: Финальный образ с Nginx ---
FROM nginx:1.27-alpine

# Копируем кастомную конфигурацию Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные статические файлы из этапа 'builder'
COPY --from=builder /app/dist /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

# Команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]