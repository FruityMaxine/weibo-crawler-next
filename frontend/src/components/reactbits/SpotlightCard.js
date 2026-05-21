import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useRef } from "react";
import { cn } from "@/lib/cn";
/**
 * SpotlightCard — 跟鼠标移动的光斑卡片 (React Bits 经典).
 */
export function SpotlightCard({ children, className, spotlightColor = "rgba(94,106,210,0.18)", }) {
    const ref = useRef(null);
    function onMove(e) {
        const el = ref.current;
        if (!el)
            return;
        const rect = el.getBoundingClientRect();
        el.style.setProperty("--x", `${e.clientX - rect.left}px`);
        el.style.setProperty("--y", `${e.clientY - rect.top}px`);
    }
    return (_jsxs("div", { ref: ref, onMouseMove: onMove, className: cn("relative overflow-hidden rounded-xl border border-hairline bg-surface", "transition-colors duration-200 hover:border-hairline-strong", className), children: [_jsx("div", { className: "pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 hover:opacity-100 group-hover:opacity-100", style: {
                    background: `radial-gradient(420px circle at var(--x) var(--y), ${spotlightColor}, transparent 40%)`,
                } }), _jsx("div", { className: "relative", children: children })] }));
}
