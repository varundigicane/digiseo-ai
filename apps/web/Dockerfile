# DigiSEO Web — Railway Root Directory = apps/web
# CLI: railway up ./apps/web --path-as-root --service web

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules

# Invalidate Railway snapshot/layer cache when the Git commit changes
ARG RAILWAY_GIT_COMMIT_SHA=dev
ARG CACHEBUST=1
RUN echo "cachebust=${CACHEBUST} commit=${RAILWAY_GIT_COMMIT_SHA}" > /tmp/.railway-build-stamp

COPY . .

# Fail the build if source context is stale (missing Subhash IA routes)
RUN test -f src/app/app/strategy/page.tsx \
    && test -f src/app/app/ai-seo/page.tsx \
    && test -f src/app/app/playbook/page.tsx \
    && ls src/app/app \
    && grep -q "AI Growth OS" src/app/page.tsx

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_APP_URL=http://localhost:3000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_APP_URL=$NEXT_PUBLIC_APP_URL \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

CMD ["sh", "-c", "node server.js"]
