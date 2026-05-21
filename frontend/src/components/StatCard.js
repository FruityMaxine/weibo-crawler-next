import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AnimatedNumber } from "@/components/reactbits/AnimatedNumber";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
export function StatCard({ label, value, icon, trend }) {
    return (_jsx(SpotlightCard, { className: "group p-5", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex flex-col gap-1", children: [_jsx("span", { className: "text-ink-subtle text-xs uppercase tracking-wider", children: label }), _jsx("span", { className: "text-3xl font-semibold text-ink tracking-tight2x", children: _jsx(AnimatedNumber, { value: value }) }), trend && _jsx("span", { className: "text-success text-xs font-mono", children: trend })] }), _jsx("div", { className: "rounded-md border border-hairline bg-surface-2 p-2 text-primary", children: icon })] }) }));
}
