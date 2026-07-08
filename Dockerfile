# ==========================
# Stage 1: Build
# ==========================
FROM node:22-bookworm AS builde

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci && \
    npm cache clean --force

# Copiar código fuente
COPY src ./src
COPY tsconfig*.json ./
COPY nest-cli.json ./

# Copiar Prisma
COPY prisma ./prisma

# Generar cliente de Prisma
RUN npx prisma generate

# Compilar la aplicación
RUN npm run build

# ==========================
# Stage 2: Runtime
# ==========================
FROM node:22-bookworm

WORKDIR /app

# Crear usuario no-root
RUN groupadd -g 1001 nodejs && \
    useradd -r -u 1001 -g nodejs nestjs

# Copiar dependencias
COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules

# Copiar aplicación compilada
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist

# Copiar Prisma
COPY --from=builder --chown=nestjs:nodejs /app/prisma ./prisma

# Cambiar al usuario no-root
USER nestjs

# Exponer puerto
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); }).on('error', () => process.exit(1));"

# Comando de inicio
CMD ["node", "dist/main"]