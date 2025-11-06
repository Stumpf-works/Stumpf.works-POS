# ================================
# Stumpf.works POS - Frontend Dockerfile
# ================================

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Default command (development mode)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
