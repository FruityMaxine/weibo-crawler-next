import { motion } from "framer-motion";
import { cn } from "@/lib/cn";

interface AuroraProps {
  className?: string;
}

/**
 * Aurora background — React Bits 风格动态渐变.
 * 用作 Dashboard / Landing 顶部 hero 背景.
 */
export function Aurora({ className }: AuroraProps) {
  return (
    <div className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      <motion.div
        className="absolute -inset-[20%] opacity-40 blur-3xl"
        style={{
          backgroundImage:
            "conic-gradient(from 90deg at 50% 50%, #5e6ad2 0deg, #828fff 60deg, #010102 180deg, #5e6ad2 300deg, #5e6ad2 360deg)",
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
      />
      <motion.div
        className="absolute -inset-[10%] opacity-30 blur-3xl mix-blend-screen"
        style={{
          backgroundImage:
            "radial-gradient(ellipse at 30% 40%, #5e6ad2 0%, transparent 60%)," +
            "radial-gradient(ellipse at 70% 60%, #27a644 0%, transparent 70%)",
        }}
        animate={{ scale: [1, 1.06, 1] }}
        transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
      />
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            "linear-gradient(180deg, transparent 0%, #010102 90%)",
        }}
      />
    </div>
  );
}
