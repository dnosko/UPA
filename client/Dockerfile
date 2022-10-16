# Pull latest official node image
FROM node:latest

# Expose ports
EXPOSE 3000

# Set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to environment variables
ENV PATH /app/node_modules/.bin:$PATH

# Copy package files and install app dependencies
COPY package.json /app/package.json
COPY yarn.lock /app/yarn.lock
RUN yarn
RUN yarn install

# Add React app to working directory
ADD . /app

# Start the React app
CMD ["npm", "start"]