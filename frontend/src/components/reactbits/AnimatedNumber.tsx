import { useEffect, useRef, useState } from "react";

interface AnimatedNumberProps {
  value: number;
  duration?: number;
  className?: string;
}

/**
 * AnimatedNumber — 数值过渡, 用于 stat 卡片.
 */
export function AnimatedNumber({ value, duration = 800, className }: AnimatedNumberProps) {
  const [display, setDisplay] = useState(value);
  const prev = useRef(value);

  useEffect(() => {
    const start = performance.now();
    const from = prev.current;
    const delta = value - from;
    if (delta === 0) return;

    let raf = 0;
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(Math.round(from + delta * eased));
      if (t < 1) raf = requestAnimationFrame(step);
      else prev.current = value;
    };
    raf = requestAnimationFrame(step);
    // v0.6.0.0: cleanup 同步 prev.current 防卸载/重 mount 时从中间值跳起
    return () => {
      cancelAnimationFrame(raf);
      prev.current = value;
    };
  }, [value, duration]);

  return <span className={className}>{display.toLocaleString()}</span>;
}
