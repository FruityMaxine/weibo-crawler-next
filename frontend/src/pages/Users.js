import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useUsers } from "@/api/hooks";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { CheckCircle2 } from "lucide-react";
export default function Users() {
    const { data, isLoading } = useUsers(100);
    if (isLoading)
        return _jsx("div", { className: "text-ink-subtle", children: "\u52A0\u8F7D\u7528\u6237..." });
    if (!data || data.length === 0) {
        return (_jsxs("div", { className: "text-center py-20 text-ink-subtle", children: ["\u6682\u65E0\u7528\u6237. \u7528 ", _jsx("code", { className: "text-primary", children: "wcn run -u <uid>" }), " \u6293\u4E00\u4E2A\u770B\u770B."] }));
    }
    return (_jsx("div", { className: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3", children: data.map((u) => (_jsxs(SpotlightCard, { className: "p-4 flex flex-col gap-2", children: [_jsxs("div", { className: "flex items-start gap-3", children: [u.avatar_hd ? (_jsx("img", { src: u.avatar_hd, alt: u.screen_name, className: "w-12 h-12 rounded-full border border-hairline", onError: (e) => (e.currentTarget.style.display = "none") })) : (_jsx("div", { className: "w-12 h-12 rounded-full bg-primary/20 grid place-items-center text-primary font-bold", children: u.screen_name.charAt(0) })), _jsxs("div", { className: "flex flex-col flex-1 min-w-0", children: [_jsxs("div", { className: "flex items-center gap-1", children: [_jsx("span", { className: "text-ink font-medium truncate", children: u.screen_name }), u.verified && _jsx(CheckCircle2, { size: 14, className: "text-primary shrink-0" })] }), _jsxs("span", { className: "text-ink-subtle text-xs font-mono", children: ["uid ", u.uid] })] })] }), u.description && (_jsx("div", { className: "text-ink-muted text-xs line-clamp-2", children: u.description })), _jsxs("div", { className: "flex gap-4 text-xs text-ink-subtle mt-1 pt-2 border-t border-hairline", children: [_jsxs("span", { children: ["\u5FAE\u535A ", _jsx("span", { className: "text-ink", children: u.statuses_count })] }), _jsxs("span", { children: ["\u7C89\u4E1D ", _jsx("span", { className: "text-ink", children: u.followers_count })] }), _jsxs("span", { children: ["\u5173\u6CE8 ", _jsx("span", { className: "text-ink", children: u.follow_count })] })] })] }, u.uid))) }));
}
