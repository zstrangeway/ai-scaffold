# Run nextjs in docker
FROM node:23-alpine-slim AS base

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
