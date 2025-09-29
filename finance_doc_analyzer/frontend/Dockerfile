# Build stage
FROM node:22-slim as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_BACKEND_API_URL
ENV VITE_BACKEND_API_URL=${VITE_BACKEND_API_URL}
RUN npm run build

# Production stage
FROM nginx:1.28.0-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d
