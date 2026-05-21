import { useRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/cn";

interface MagneticButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  strength?: number;
  variant?: "primary" | "ghost";
}

/**
 * MagneticButton — 鼠标靠近时按钮位移吸附 (React Bits).
 */
export function MagneticButton({
  children,
  strength = 18,
  variant = "primary",
  className,
  ...rest
}: MagneticButtonProps) {
  const ref = useRef<HTMLButtonElement>(null);

  return (
    <button
      ref={ref}
      onMouseMove={(e) => {
        const el = ref.current;
        if (!el) return;
        const rect = el.getBoundingClientRect();
        const dx = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2);
        const dy = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2);
        el.style.transform = `translate3d(${dx * strength}px, ${dy * strength}px, 0)`;
      }}
      onMouseLeave={() => {
        const el = ref.current;
        if (el) el.style.transform = "translate3d(0,0,0)";
      }}
      className={cn(
        "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-all duration-200",
        "will-change-transform",
        variant === "primary"
          ? "bg-primary text-white hover:bg-primary-hover focus:ring-2 focus:ring-primary-focus"
          : "border border-hairline bg-surface text-ink hover:border-hairline-strong hover:bg-surface-2",
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}
