FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

# Accept the secret admin route at build time so Vite can inline it.
# Set ADMIN_ROUTE in .env or docker-compose to a hard-to-guess path.
ARG VITE_ADMIN_ROUTE
ENV VITE_ADMIN_ROUTE=$VITE_ADMIN_ROUTE

COPY . .
RUN npm run build

# Production image
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
