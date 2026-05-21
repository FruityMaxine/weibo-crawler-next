import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { useSearch } from "@/api/hooks";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { Search as SearchIcon } from "lucide-react";
export default function Search() {
    const [q, setQ] = useState("");
    const [submitted, setSubmitted] = useState("");
    const { data, isLoading } = useSearch(submitted);
    return (_jsxs("div", { className: "flex flex-col gap-4", children: [_jsxs("form", { onSubmit: (e) => {
                    e.preventDefault();
                    setSubmitted(q.trim());
                }, className: "flex gap-2", children: [_jsxs("div", { className: "flex-1 relative", children: [_jsx(SearchIcon, { size: 16, className: "absolute left-3 top-1/2 -translate-y-1/2 text-ink-subtle" }), _jsx("input", { className: "w-full bg-surface-2 border border-hairline rounded-md pl-9 pr-3 py-2.5 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary", placeholder: "FTS5 \u8868\u8FBE\u5F0F: '\u7F16\u7A0B' / '\u7F16\u7A0B AND Python' / 'Python OR Rust'", value: q, onChange: (e) => setQ(e.target.value) })] }), _jsx("button", { type: "submit", className: "bg-primary text-white px-5 rounded-md text-sm font-medium hover:bg-primary-hover transition-colors", children: "\u641C\u7D22" })] }), submitted && (_jsxs("div", { className: "text-ink-subtle text-xs", children: ["query: ", _jsx("code", { className: "text-primary", children: submitted }), data ? ` · ${data.count} 命中` : ""] })), isLoading && _jsx("div", { className: "text-ink-subtle", children: "\u641C\u7D22\u4E2D..." }), _jsxs("div", { className: "flex flex-col gap-3", children: [data?.hits.map((h) => (_jsxs(SpotlightCard, { className: "p-4", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsxs("div", { className: "text-ink-subtle text-xs font-mono", children: [h.weibo_id, " \u00B7 uid ", h.uid, " \u00B7 score ", h.score.toFixed(2)] }), _jsx("span", { className: "text-ink-subtle text-xs", children: h.created_at ? new Date(h.created_at).toLocaleString() : "" })] }), _jsx("div", { className: "text-ink text-sm leading-relaxed", dangerouslySetInnerHTML: { __html: h.snippet || h.text } })] }, h.weibo_id))), submitted && data?.count === 0 && (_jsx("div", { className: "text-center py-12 text-ink-subtle", children: "\u6CA1\u627E\u5230\u5339\u914D\u9879. \u8BD5\u8BD5\u66F4\u7B80\u77ED\u7684\u5173\u952E\u8BCD." }))] })] }));
}
