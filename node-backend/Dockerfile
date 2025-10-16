# === STAGE 1: BUILD (Install Dependencies) ===
# Use a current, stable Node.js image
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy the package files
COPY package.json .
COPY package-lock.json .

# Install dependencies. We specifically exclude devDependencies 
# (like nodemon) which aren't needed for the final production image.
RUN npm install --production
Run npm install redis

# === STAGE 2: PRODUCTION (Copy Code and Run) ===
# Use a minimal Node.js image for the final runtime
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy only the production dependencies from the builder stage
COPY --from=builder /app/node_modules ./node_modules

# Copy the server code
COPY server.js .

# Expose the port the Node.js server is listening on
# (This matches the 4000 you defined in server.js)
EXPOSE 4000

# Set the command to run the application (in production mode)
CMD ["node", "server.js"]