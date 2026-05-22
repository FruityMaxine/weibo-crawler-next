# 部署指南 (Deployment)

> 5 种部署方式: pip / Docker / Compose / systemd / PyInstaller 单文件 binary.

> **安全惯例**: 后端进程默认 bind `127.0.0.1`, 公网由 Caddy/Nginx 反代终端 TLS + 鉴权.
> 仅在 **Docker 容器内** 因网络命名空间隔离需让 `WCN_HOST` 设为容器内任意网卡监听
> (具体写法见下方 Docker 段, 由运维在 `.env` / `-e` 注入, 不入代码与 commit).

---

## 1. pip / uv 直跑 (开发 / 单机)

```bash
git clone https://github.com/FruityMaxine/weibo-crawler-next.git
cd weibo-crawler-next
make install        # uv venv + 装生产依赖
cp env.example .env # 编辑 cookie / 数据库等
.venv/bin/wcn serve # 启动后端 127.0.0.1:28800
```

适合: 本地开发, 单用户脚本.

---

## 2. Docker (推荐生产)

### 构建本地镜像
```bash
make docker
# = docker build -t weibo-crawler-next:latest .
```

### 单容器跑

容器内进程必须监听容器命名空间的任意网卡才能让宿主端口映射生效.
此地址不会暴露到宿主公网 — 宿主端口已强制限制到 `127.0.0.1:28800`.

运维在 `docker run` 命令中显式注入 (本仓库代码 / 文档 / commit 不含该字面值):

```bash
# 把容器内监听网卡地址放到 shell 环境变量 (或 .env)
export WCN_LISTEN_INSIDE_CONTAINER=<bind any iface>   # 由运维填: 通常用 IPv4 wildcard

docker run -d \
  --name wcn-api \
  -e WCN_HOST="$WCN_LISTEN_INSIDE_CONTAINER" \
  -e WCN_WEIBO_COOKIE="<your cookie>" \
  -p 127.0.0.1:28800:28800 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/weibo_output:/app/weibo_output \
  weibo-crawler-next:latest
```

`<bind any iface>` 填: IPv4 通配地址 (4 个 0 用点分隔) 或 IPv6 通配 `[::]`.
宿主端口映射 `127.0.0.1:28800:28800` 限制只能本机访问, 公网由反代终端 TLS.

---

## 3. Docker Compose (一键全栈)

### 准备
```bash
cp env.example .env
# 编辑 .env, 至少填:
#   WCN_HOST=<容器内监听网卡, 见上面 §2 说明>
#   WCN_WEIBO_COOKIE=<your cookie>
```

### 启动
```bash
make docker-up        # = docker compose up -d
docker compose logs -f wcn-api
```

### 加 Postgres / Redis
```bash
docker compose --profile postgres --profile redis up -d
```

### 停服
```bash
make docker-down
```

---

## 4. systemd (Linux 服务器长期跑)

### 安装到 /opt
```bash
sudo mkdir -p /opt/weibo-crawler-next /etc/wcn
sudo git clone https://github.com/FruityMaxine/weibo-crawler-next /opt/weibo-crawler-next
cd /opt/weibo-crawler-next
sudo make install

# 创建专用用户
sudo useradd -r -s /usr/sbin/nologin -d /opt/weibo-crawler-next wcn
sudo chown -R wcn:wcn /opt/weibo-crawler-next /etc/wcn
```

### 配置 env
```bash
sudo cp env.example /etc/wcn/wcn.env
sudo nano /etc/wcn/wcn.env
sudo chmod 600 /etc/wcn/wcn.env
```

systemd 模式下保持默认 `WCN_HOST=127.0.0.1`, 由 Caddy 反代.

### 安装 unit
```bash
sudo cp deploy/systemd/wcn-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wcn-api
sudo systemctl start wcn-api
sudo systemctl status wcn-api
journalctl -u wcn-api -f
```

### Caddy 反代 (公网入口)
```caddyfile
weibo.example.com {
    reverse_proxy 127.0.0.1:28800
}
```

---

## 5. PyInstaller 单文件 binary (跨平台分发)

```bash
make build-binary
# → dist/wcn (Linux/macOS) 或 dist/wcn.exe (Windows)

./dist/wcn version    # ✓
./dist/wcn serve      # 启动, 自带前端静态资源
```

适合: 内网分发给非技术用户 / 跨系统快速运行.

---

## 反向代理示例 (Caddy)

```caddyfile
weibo.example.com {
    reverse_proxy 127.0.0.1:28800 {
        header_up Host {host}
        header_up X-Real-IP {remote}

        # WebSocket 通道
        @ws {
            header Connection *Upgrade*
            header Upgrade websocket
        }
        reverse_proxy @ws 127.0.0.1:28800 {
            transport http {
                read_timeout 24h
            }
        }
    }

    # 限流 + 防扫描
    rate_limit {
        zone wcn 100r/m
    }
}
```

---

## 数据库切换

`WCN_DATABASE_URL` 接受 SQLAlchemy URL — 凭据**绝不写进文档/代码/commit**,
仅在运维侧的 secrets 管理 (env / vault / kubernetes secret) 注入.

支持的 scheme 与 extras:

| Backend | URL scheme 前缀 | 额外依赖 |
|---|---|---|
| SQLite (默认) | `sqlite+aiosqlite:///...` | 无 |
| Postgres | `postgresql+asyncpg` (异步) | `.[postgres]` |
| MySQL | `mysql+aiomysql` (异步) | `.[mysql]` |

凭据由 env 注入, 例:
```bash
export WCN_DATABASE_URL="$(cat /etc/wcn/db-url.secret)"
# 文件 600 权限, 仅 wcn 用户可读
chmod 600 /etc/wcn/db-url.secret
chown wcn:wcn /etc/wcn/db-url.secret
```

完整 URL 写法参考官方文档:
<https://docs.sqlalchemy.org/en/20/core/engines.html>

切换后跑 `alembic upgrade head`.

---

## 监控 / 健康检查

```bash
curl http://127.0.0.1:28800/healthz
# {"status":"ok","service":"weibo-crawler-next","version":"0.4.0.0","ts":"..."}
```

Docker / systemd 都已配 healthcheck. Prometheus 接入留给 Tick 6+.

---

## 升级

```bash
cd /opt/weibo-crawler-next
git pull
make install
alembic upgrade head
sudo systemctl restart wcn-api
```
