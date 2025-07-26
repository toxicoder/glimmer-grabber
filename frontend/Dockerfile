# Use an official Node.js runtime as a parent image
FROM node:16-alpine as build

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY my-react-app/package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application's code
COPY my-react-app/ .

# Build the React application
RUN npm run build

# Use a smaller, more secure image for serving the built application
FROM nginx:alpine

# Copy the built assets from the build stage to the Nginx html directory
COPY --from=build /usr/src/app/dist /usr/share/nginx/html

# Expose port 80 to the outside world
EXPOSE 80

# Command to run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
