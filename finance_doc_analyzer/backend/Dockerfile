FROM node:22-slim

# Set working directory
WORKDIR /app

# Copy package files first
COPY package*.json ./

# Install dependencies
RUN npm install --omit=dev

# Copy backend code
COPY . .

# Expose backend port
EXPOSE 5050

# Run server
CMD ["node", "server.js"]
