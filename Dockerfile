# Stage 1: Build
FROM node:22-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production && \
    npm cache clean --force

# Copiar código fuente
COPY src ./src
COPY tsconfig*.json ./
COPY nest-cli.json ./

# Compilar la aplicación
RUN npm run build

# Stage 2: Runtime
FROM node:22-alpine

WORKDIR /app

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nestjs -u 1001

# Copiar node_modules de la etapa de build
COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules

# Copiar el dist compilado
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist

# Cambiar al usuario nestjs
USER nestjs

# Exponer puerto
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (res) => { if (res.statusCode !== 200 || res.statusCode === 404) throw new Error('health check failed'); })" || exit 1

# Comando de inicio
CMD ["node", "dist/main"]
