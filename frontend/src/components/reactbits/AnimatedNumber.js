import { jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useRef, useState } from "react";
/**
 * AnimatedNumber — 数值过渡, 用于 stat 卡片.
 */
export function AnimatedNumber({ value, duration = 800, className }) {
    const [display, setDisplay] = useState(value);
    const prev = useRef(value);
    useEffect(() => {
        const start = performance.now();
        const from = prev.current;
        const delta = value - from;
        if (delta === 0)
            return;
        let raf = 0;
        const step = (now) => {
            const t = Math.min(1, (now - start) / duration);
            // ease-out cubic
            const eased = 1 - Math.pow(1 - t, 3);
            setDisplay(Math.round(from + delta * eased));
            if (t < 1)
                raf = requestAnimationFrame(step);
            else
                prev.current = value;
        };
        raf = requestAnimationFrame(step);
        return () => cancelAnimationFrame(raf);
    }, [value, duration]);
    return _jsx("span", { className: className, children: display.toLocaleString() });
}
