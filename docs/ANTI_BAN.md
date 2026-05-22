# 反封禁策略 (Anti-Ban)

> 微博风控对高频抓取很敏感. 本项目用 5 子系统 + 自适应策略减少被封风险.

---

## 5 子系统总览

```
        ┌─────────────────────────────────────────┐
        │           AsyncWeiboClient              │
        └──────┬──────────┬──────────┬────────────┘
               │          │          │
       ┌───────▼───┐ ┌────▼────┐ ┌───▼────────┐
       │ Cookie    │ │ Proxy   │ │ UA + 设备  │
       │ Pool      │ │ Pool    │ │ 指纹随机   │
       └───────────┘ └─────────┘ └────────────┘
               │          │          │
               └────┬─────┴──────────┘
                    │
            ┌───────▼─────────┐
            │ TokenBucketLimiter│
            │  + 自适应延时    │
            │  + 429 退避     │
            └───────┬─────────┘
                    │
            ┌───────▼─────────┐
            │ Captcha Detector│
            │  + 响应分析     │
            └─────────────────┘
```

---

## 1. Cookie 池 (`anti_ban/cookie_pool.py`)

### 核心算法
- **加权随机**: 每条 cookie 用 `health ** 2` 作为权重选择.
- **健康度 EMA**: 每次结果按 `health = 0.7 * health + 0.3 * (1.0 if success else 0)`.
- **连续失败屏蔽**: 连续 3 次失败 → 指数冷却 (60s, 120s, 240s, ..., 上限 30 min).

### 用法
```python
from backend.app.anti_ban import CookiePool
from backend.app.crawler import AsyncWeiboClient

pool = CookiePool([
    ("SUB=xxx;SUBP=yyy;...", "account1"),
    ("SUB=aaa;SUBP=bbb;...", "account2"),
])

async with AsyncWeiboClient(cookie_pool=pool) as client:
    info = await client.get_user_info(1669879400)

print(pool.stats())  # 看每条 cookie 健康度
```

### 何时屏蔽 cookie
- HTTP 429 / 403
- 微博 ok=0 含"验证码 / 异地登录 / 频繁操作" 关键词
- httpx 网络层错误连续 3 次

---

## 2. Proxy 池 (`anti_ban/proxy_pool.py`)

### 核心算法
- **加权**: `health ** 2 / (1 + latency_ms/1000)`, 优选健康度高 + 延迟低.
- **探活**: `pool.probe_all()` 异步探活所有代理 (默认探 `m.weibo.cn/`), 更新延迟与健康度.
- **失败降权**: 连续 2 次失败 → 90s → 180s → ... → 上限 1h 冷却.

### 用法
```python
pool = ProxyPool([
    "http://10.0.0.1:8080",
    "socks5://10.0.0.2:1080",
])
await pool.probe_all()    # 启动时探活
async with AsyncWeiboClient(proxy_pool=pool) as client: ...
```

可结合 vega-proxy 项目用作多国家 IP 出口.

---

## 3. UA + 设备指纹 (`anti_ban/ua_pool.py`)

- 8 条 2026 年真实 UA (iPhone Safari / Android Chrome / Desktop)
- 默认 70% 移动端 + 30% 桌面 (m.weibo.cn 偏好移动端)
- `random_device_fingerprint()` 生成 `Sec-CH-UA-*` / `Device-Memory` / `X-Request-Id` 随机化

每次请求自动注入到 headers, 配合 cookie 轮换让"设备 + 账号"组合不固定.

---

## 4. TokenBucketLimiter (`anti_ban/rate_limiter.py`)

替换 Tick 2 的简易固定 sleep, 升级为 Token Bucket + 自适应:

### Token Bucket
- 容量 `burst` (默认 3), 速率 `rate` (默认从 .env 读, 1.0 req/sec)
- `acquire()` 阻塞到拿到 1 token

### 自适应
- `report_response_time(ms)`: EMA 跟踪平均响应时间
  - 平均 < 500ms 且未到上限 → 速率 *1.1 (加速)
  - 平均 > 2000ms → 速率 *0.8 (降速)

### 429 退避
- `report_rate_limited()` 触发指数退避: 5s → 10s → 20s → ... → 上限 5 min
- 同时永久降速 (current_rate *= 0.5)
- 连续成功后 (`report_success()`) 才重置计数

---

## 5. Captcha Detector (`anti_ban/captcha_detector.py`)

- `detect_captcha(payload)`: 扫描响应中"验证码 / 异地登录 / 操作过于频繁" 等关键词
- `is_rate_limited(status, payload)`: HTTP 429/418 或 captcha 关键词 → True

```python
if is_rate_limited(resp.status_code, resp.text):
    limiter.report_rate_limited()
    cookie_pool.release(entry, success=False)
```

---

## 实战配置示例

```bash
# .env
WCN_CRAWLER_RATE_LIMIT=0.8        # 慢一点更稳
WCN_CRAWLER_TIMEOUT=30
WCN_CRAWLER_RETRY_MAX=5

# 多账号 cookie (Tick 5 提供 Python API, Tick 6+ 提供 wcn cookie-pool add CLI 命令)
```

```python
# 自定义 client
from backend.app.anti_ban import CookiePool, ProxyPool, UAPool
from backend.app.crawler import AsyncWeiboClient

cookie_pool = CookiePool([("SUB=...", "main"), ("SUB=...", "backup")])
proxy_pool = ProxyPool(["http://...", "socks5://..."])
await proxy_pool.probe_all()
ua_pool = UAPool(mobile_weight=0.85)

async with AsyncWeiboClient(
    cookie_pool=cookie_pool,
    proxy_pool=proxy_pool,
    ua_pool=ua_pool,
) as client:
    ...
```

---

## 监控

`/api/anti_ban/stats` (Tick 6 暴露) 将提供:
- 每条 cookie 的健康度 / 使用次数 / 冷却剩余
- 每个代理的延迟 / 健康度 / 失败统计
- 限频器当前速率 / EMA 响应时间 / 连续 429 计数

---

## 已知限制

- 验证码出现时不会自动绕过 (打码平台接入留 Tick 6+)
- 没有"模拟浏览器" 级行为模拟 (后续可接 Playwright)
- 不支持微博的 OAuth 流程, 仅用 cookie 注入

---

## 最佳实践

1. **配多账号** — 单账号一旦风控全部失败, 多账号轮换可降级.
2. **配代理 + 多 cookie** — 让"账号 × IP" 组合数量大.
3. **限频别太快** — 默认 1 req/sec, 抓量大时调到 0.5 req/sec.
4. **晚上跑** — 微博风控阈值动态调整, 低峰期更宽容.
5. **遇到验证码立即停** — 别硬撞, 让限频退避起作用.
