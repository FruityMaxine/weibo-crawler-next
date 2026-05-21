import { SpotlightCard } from "@/components/reactbits/SpotlightCard";

const GROUPS: { title: string; desc: string; fields: { k: string; v: string }[] }[] = [
  {
    title: "运行环境",
    desc: ".env / 环境变量配置, 修改后重启 wcn serve",
    fields: [
      { k: "WCN_ENV", v: "dev" },
      { k: "WCN_HOST", v: "127.0.0.1 (铁律: 不绑 0.0.0.0)" },
      { k: "WCN_PORT", v: "28800" },
      { k: "WCN_LOG_LEVEL", v: "INFO" },
    ],
  },
  {
    title: "数据存储",
    desc: "默认 SQLite + FTS5, 可切 Postgres/MySQL",
    fields: [
      { k: "WCN_DATABASE_URL", v: "sqlite+aiosqlite:///./data/wcn.db" },
      { k: "WCN_DATA_DIR", v: "./data" },
      { k: "WCN_OUTPUT_DIR", v: "./weibo_output" },
    ],
  },
  {
    title: "抓取参数",
    desc: "全局抓取速率与超时",
    fields: [
      { k: "WCN_CRAWLER_RATE_LIMIT", v: "1.0 req/sec" },
      { k: "WCN_CRAWLER_TIMEOUT", v: "20 sec" },
      { k: "WCN_CRAWLER_RETRY_MAX", v: "3" },
      { k: "WCN_CRAWLER_PAGE_SIZE", v: "10" },
    ],
  },
  {
    title: "导出 (Tick 3)",
    desc: "默认 CSV 格式, 可选 6 种",
    fields: [
      { k: "WCN_EXPORT_DEFAULT_FORMAT", v: "csv" },
      { k: "WCN_EXPORT_REMOVE_HTML", v: "true" },
      { k: "WCN_EXPORT_INCLUDE_RETWEET", v: "true" },
    ],
  },
  {
    title: "敏感凭据",
    desc: "WEIBO_COOKIE / MYSQL_PASSWORD / WEBHOOK_TOKEN 应只从 env 注入, 不入 git",
    fields: [
      { k: "WCN_WEIBO_COOKIE", v: "•••••• (env)" },
      { k: "WCN_MYSQL_PASSWORD", v: "•••••• (env)" },
      { k: "WCN_WEBHOOK_TOKEN", v: "•••••• (env)" },
      { k: "WCN_MONGODB_URI", v: "•••••• (env)" },
    ],
  },
];

export default function Settings() {
  return (
    <div className="flex flex-col gap-4">
      <div className="text-ink-muted text-sm">
        当前为只读视图. 编辑请改 <code className="text-primary">.env</code>
        {" 或 "}
        <code className="text-primary">config.yaml</code> 后重启 <code className="text-primary">wcn serve</code>.
      </div>
      {GROUPS.map((g) => (
        <SpotlightCard key={g.title} className="p-5">
          <div className="mb-3">
            <h3 className="text-ink font-semibold">{g.title}</h3>
            <p className="text-ink-subtle text-xs mt-0.5">{g.desc}</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {g.fields.map((f) => (
              <div
                key={f.k}
                className="flex justify-between border border-hairline rounded-md px-3 py-2 bg-surface-2"
              >
                <code className="text-ink-muted text-xs font-mono">{f.k}</code>
                <span className="text-ink text-xs font-mono">{f.v}</span>
              </div>
            ))}
          </div>
        </SpotlightCard>
      ))}
    </div>
  );
}
