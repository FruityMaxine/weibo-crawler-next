# weibo-crawler-next — multi-stage Dockerfile
# - Stage 1: 用 uv 构建后端依赖
# - Stage 2: 用 Node 构建前端静态资源
# - Stage 3: 最终镜像 (python:slim + uv + 前端 dist)
#
# 注: 容器内 bind 地址由运维通过 -e WCN_HOST=... 或 .env 注入,
#     代码内不写死 wildcard 地址 (默认沿用 settings.py 的 127.0.0.1).
#     docker / compose 部署时用户须显式设置 WCN_HOST 监听任意网卡,
#     宿主端口映射限制到 127.0.0.1:28800 由 Caddy 反代到公网.

# ===== Stage 1: backend builder =====
FROM python:3.12-slim AS backend-builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build
COPY pyproject.toml ./
COPY backend ./backend
COPY cli ./cli
COPY README.md LICENSE ./

RUN uv venv /opt/venv --python 3.12 \
    && VIRTUAL_ENV=/opt/venv uv pip install --no-cache .

# ===== Stage 2: frontend builder =====
FROM node:22-alpine AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --silent

COPY frontend/ ./
RUN npm run build

# ===== Stage 3: runtime =====
FROM python:3.12-slim AS runtime

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends curl tini ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -u 1000 -m -d /app -s /bin/sh wcn

COPY --from=backend-builder /opt/venv /opt/venv
COPY --from=backend-builder /build/backend /app/backend
COPY --from=backend-builder /build/cli /app/cli
COPY --from=backend-builder /build/pyproject.toml /build/README.md /build/LICENSE /app/

COPY --from=frontend-builder /build/frontend/dist /app/frontend/dist

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WCN_PORT=28800 \
    WCN_DATA_DIR=/app/data \
    WCN_OUTPUT_DIR=/app/weibo_output

WORKDIR /app
RUN mkdir -p /app/data /app/weibo_output && chown -R wcn:wcn /app

USER wcn
EXPOSE 28800

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:28800/healthz || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["wcn", "serve"]
