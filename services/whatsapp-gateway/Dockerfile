FROM node:20-alpine

WORKDIR /app

# Install deps first for layer caching
COPY package.json ./
RUN npm install --omit=dev

COPY src/ ./src/

ENV NODE_ENV=production
ENV WA_GATEWAY_PORT=3100

EXPOSE 3100

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD wget -qO- http://localhost:3100/health/ || exit 1

CMD ["node", "src/index.js"]
