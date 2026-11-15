# ---------- Étape 1 : l'atelier (compiler Angular) ----------
FROM node:22-alpine AS atelier

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- Étape 2 : la vitrine (servir avec Nginx) ----------
FROM nginxinc/nginx-unprivileged:stable-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=atelier /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 8080