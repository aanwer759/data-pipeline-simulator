# === STAGE 1: BUILD THE REACT APPLICATION ===
# Use a Node.js base image to perform the build
FROM node:20-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to install dependencies
COPY package.json .
COPY package-lock.json .

# Install dependencies
RUN npm install

# Copy all other source files (including src, public, etc.)
COPY . .

# Run the production build command
# The resulting static files will be placed in the 'build' folder (for CRA)
# If using Vite, replace 'build' with 'dist'
RUN npm run build 


# === STAGE 2: SERVE WITH NGINX ===
# Use a lightweight Nginx image as the final server
FROM docker.io/nginx

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy a custom Nginx configuration (see Step 3 below)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the static build files from the 'builder' stage into the Nginx server directory
# NOTE: If using Vite, replace '/app/build' with '/app/dist'
COPY --from=builder /app/build /usr/share/nginx/html

# Expose the standard HTTP port
EXPOSE 80

# The default Nginx CMD will start the server
CMD ["nginx", "-g", "daemon off;"]