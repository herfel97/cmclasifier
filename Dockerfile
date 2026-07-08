# ==========================
# Stage 1: Build
# ==========================
FROM node:22-bookworm AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Copiar Prisma antes de la instalación por si algún script de instalación lo necesita
COPY prisma ./prisma

# Instalar dependencias (asegurar ejecución de postinstall dentro del contenedor)
RUN npm ci --unsafe-perm && \
    npm cache clean --force

# Copiar código fuente
COPY src ./src
COPY tsconfig*.json ./
COPY nest-cli.json ./

# Asegurar binarios nativos/paquetes de prisma estén reconstruidos (defensa adicional)
RUN npm rebuild @prisma/client || true

# Generar cliente de Prisma
RUN npx prisma generate --schema=./prisma/schema.prisma
RUN ls -la node_modules/.prisma/client || true

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