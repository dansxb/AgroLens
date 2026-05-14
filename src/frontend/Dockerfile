# ============================================================
# AgroLens Frontend — Multi-stage Dockerfile
# Base image: Node 20 Alpine
# ============================================================

# -----------------------------------------------------------
# Stage 1: dependency installer
# -----------------------------------------------------------
FROM node:20-alpine AS deps

RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci --frozen-lockfile; else npm install; fi


# -----------------------------------------------------------
# Stage 2: development image
# Source code mounted as a volume for hot-reload
# -----------------------------------------------------------
FROM node:20-alpine AS development

ENV NODE_ENV=development

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# In development, source is mounted via docker-compose volume.
# We only copy package.json here as a cache reference.
COPY package.json ./

EXPOSE 3000

CMD ["npm", "run", "dev"]


# -----------------------------------------------------------
# Stage 3: builder (for production)
# -----------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the Next.js application
# NEXT_PUBLIC_* variables must be available at build time
ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_MAPBOX_TOKEN
ARG NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
ARG NEXT_PUBLIC_SENTRY_DSN
ARG NEXT_PUBLIC_ENVIRONMENT

ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL \
    NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL \
    NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY \
    NEXT_PUBLIC_MAPBOX_TOKEN=$NEXT_PUBLIC_MAPBOX_TOKEN \
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY \
    NEXT_PUBLIC_SENTRY_DSN=$NEXT_PUBLIC_SENTRY_DSN \
    NEXT_PUBLIC_ENVIRONMENT=$NEXT_PUBLIC_ENVIRONMENT

RUN npm run build


# -----------------------------------------------------------
# Stage 4: production runner
# Minimal image; runs as non-root
# -----------------------------------------------------------
FROM node:20-alpine AS production

ENV NODE_ENV=production

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy built artefacts
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:3000/ | grep -q AgroLens || exit 1

CMD ["node", "server.js"]
