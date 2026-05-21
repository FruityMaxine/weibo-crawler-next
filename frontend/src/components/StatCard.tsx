import type { ReactNode } from "react";
import { AnimatedNumber } from "@/components/reactbits/AnimatedNumber";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";

interface StatCardProps {
  label: string;
  value: number;
  icon: ReactNode;
  trend?: string;
}

export function StatCard({ label, value, icon, trend }: StatCardProps) {
  return (
    <SpotlightCard className="group p-5">
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <span className="text-ink-subtle text-xs uppercase tracking-wider">{label}</span>
          <span className="text-3xl font-semibold text-ink tracking-tight2x">
            <AnimatedNumber value={value} />
          </span>
          {trend && <span className="text-success text-xs font-mono">{trend}</span>}
        </div>
        <div className="rounded-md border border-hairline bg-surface-2 p-2 text-primary">
          {icon}
        </div>
      </div>
    </SpotlightCard>
  );
}
