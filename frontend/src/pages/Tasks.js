import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { useTasks, useCreateTask } from "@/api/hooks";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { MagneticButton } from "@/components/reactbits/MagneticButton";
import { Plus } from "lucide-react";
export default function Tasks() {
    const { data, isLoading, error } = useTasks();
    const create = useCreateTask();
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ name: "", uid: "", max_count: 50 });
    async function submit() {
        if (!form.name.trim() || !form.uid.trim())
            return;
        try {
            await create.mutateAsync({
                name: form.name,
                uid: Number(form.uid),
                max_count: form.max_count,
            });
            setShowForm(false);
            setForm({ name: "", uid: "", max_count: 50 });
        }
        catch (e) {
            alert("创建失败: " + String(e));
        }
    }
    return (_jsxs("div", { className: "flex flex-col gap-4", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("p", { className: "text-ink-muted text-sm", children: "\u91C7\u96C6\u4EFB\u52A1\u4EE5\u5F02\u6B65\u540E\u53F0\u8FD0\u884C, \u8FDB\u5EA6\u901A\u8FC7 WS \u5B9E\u65F6\u63A8\u9001." }), _jsxs(MagneticButton, { onClick: () => setShowForm(true), className: "inline-flex items-center gap-1.5", children: [_jsx(Plus, { size: 14 }), " \u65B0\u5EFA\u4EFB\u52A1"] })] }), showForm && (_jsxs(SpotlightCard, { className: "p-5 space-y-3", children: [_jsx("h3", { className: "font-semibold text-ink", children: "\u65B0\u5EFA\u91C7\u96C6\u4EFB\u52A1" }), _jsx("input", { className: "w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary", placeholder: "\u4EFB\u52A1\u540D\u79F0, e.g. \u5468\u672B\u6293 X \u7528\u6237", value: form.name, onChange: (e) => setForm({ ...form, name: e.target.value }) }), _jsx("input", { className: "w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary", placeholder: "\u5FAE\u535A UID, e.g. 1669879400", value: form.uid, onChange: (e) => setForm({ ...form, uid: e.target.value }) }), _jsx("input", { type: "number", className: "w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary", placeholder: "\u6700\u5927\u6761\u6570", value: form.max_count, onChange: (e) => setForm({ ...form, max_count: Number(e.target.value) }) }), _jsxs("div", { className: "flex gap-2", children: [_jsx(MagneticButton, { onClick: submit, children: "\u521B\u5EFA\u5E76\u542F\u52A8" }), _jsx(MagneticButton, { variant: "ghost", onClick: () => setShowForm(false), children: "\u53D6\u6D88" })] })] })), isLoading && _jsx("div", { className: "text-ink-subtle text-sm", children: "\u52A0\u8F7D\u4EFB\u52A1..." }), error && _jsxs("div", { className: "text-danger text-sm", children: ["\u52A0\u8F7D\u5931\u8D25: ", String(error)] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-3", children: [data?.map((t) => (_jsxs(SpotlightCard, { className: "p-4", children: [_jsxs("div", { className: "flex justify-between items-start mb-2", children: [_jsxs("div", { children: [_jsxs("div", { className: "text-ink font-medium", children: ["#", t.id, " ", t.name] }), _jsxs("div", { className: "text-ink-subtle text-xs", children: ["uid ", t.uid ?? "—", " \u00B7 \u521B\u5EFA ", new Date(t.created_at).toLocaleString()] })] }), _jsx("span", { className: `text-xs px-2 py-0.5 rounded font-mono ${t.status === "success" ? "bg-success/15 text-success"
                                            : t.status === "failed" ? "bg-danger/15 text-danger"
                                                : t.status === "running" ? "bg-primary/15 text-primary animate-pulse-glow"
                                                    : "bg-surface-2 text-ink-subtle"}`, children: t.status })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "flex-1 h-2 bg-surface-2 rounded-full overflow-hidden", children: _jsx("div", { className: "h-full bg-primary transition-all duration-500", style: { width: `${t.progress}%` } }) }), _jsxs("span", { className: "font-mono text-xs text-ink-muted w-10", children: [t.progress, "%"] })] }), _jsxs("div", { className: "text-ink-subtle text-xs mt-2", children: ["\u5DF2\u6293 ", t.total_fetched, " \u6761"] }), t.error && (_jsx("div", { className: "mt-2 text-danger text-xs font-mono break-all", children: t.error.slice(0, 200) }))] }, t.id))), data?.length === 0 && (_jsx("div", { className: "col-span-full text-center py-12 text-ink-subtle", children: "\u6682\u65E0\u4EFB\u52A1. \u70B9\u51FB\u53F3\u4E0A [\u65B0\u5EFA\u4EFB\u52A1] \u521B\u5EFA\u7B2C\u4E00\u4E2A." }))] })] }));
}
