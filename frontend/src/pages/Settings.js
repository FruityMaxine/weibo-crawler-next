import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
const GROUPS = [
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
    return (_jsxs("div", { className: "flex flex-col gap-4", children: [_jsxs("div", { className: "text-ink-muted text-sm", children: ["\u5F53\u524D\u4E3A\u53EA\u8BFB\u89C6\u56FE. \u7F16\u8F91\u8BF7\u6539 ", _jsx("code", { className: "text-primary", children: ".env" }), " 或 ", _jsx("code", { className: "text-primary", children: "config.yaml" }), " \u540E\u91CD\u542F ", _jsx("code", { className: "text-primary", children: "wcn serve" }), "."] }), GROUPS.map((g) => (_jsxs(SpotlightCard, { className: "p-5", children: [_jsxs("div", { className: "mb-3", children: [_jsx("h3", { className: "text-ink font-semibold", children: g.title }), _jsx("p", { className: "text-ink-subtle text-xs mt-0.5", children: g.desc })] }), _jsx("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-2", children: g.fields.map((f) => (_jsxs("div", { className: "flex justify-between border border-hairline rounded-md px-3 py-2 bg-surface-2", children: [_jsx("code", { className: "text-ink-muted text-xs font-mono", children: f.k }), _jsx("span", { className: "text-ink text-xs font-mono", children: f.v })] }, f.k))) })] }, g.title)))] }));
}
