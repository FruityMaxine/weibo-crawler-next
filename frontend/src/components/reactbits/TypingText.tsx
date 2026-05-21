import { useEffect, useState } from "react";

interface TypingTextProps {
  text: string;
  speed?: number;
  className?: string;
  cursor?: boolean;
}

/**
 * TypingText — 打字机效果, 用于 Hero 标题 (React Bits).
 */
export function TypingText({ text, speed = 40, className, cursor = true }: TypingTextProps) {
  const [shown, setShown] = useState("");

  useEffect(() => {
    setShown("");
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setShown(text.slice(0, i));
      if (i >= text.length) clearInterval(id);
    }, speed);
    return () => clearInterval(id);
  }, [text, speed]);

  return (
    <span className={className}>
      {shown}
      {cursor && (
        <span className="ml-1 inline-block h-[1em] w-[2px] -mb-[2px] bg-primary animate-pulse-glow" />
      )}
    </span>
  );
}
