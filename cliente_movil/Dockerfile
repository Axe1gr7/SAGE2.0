FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all project files
COPY . .

# Expose Metro bundler port
EXPOSE 8081

# Start the Expo Metro Bundler server
CMD ["npx", "expo", "start", "--lan"]
