import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { Terminal } from "lucide-react";

export default function Logs() {
  return (
    <SpotlightCard className="p-5">
      <div className="flex items-center gap-2 mb-4">
        <Terminal size={16} className="text-primary" />
        <h3 className="text-ink font-semibold">日志查看</h3>
      </div>
      <div className="text-ink-muted text-sm mb-3">
        默认日志输出 stderr (uvicorn / APScheduler / wcn). 启用文件日志:
      </div>
      <pre className="bg-surface-2 border border-hairline rounded-md p-3 text-xs font-mono text-ink-muted overflow-x-auto">
{`# .env 中加入
WCN_LOG_FILE=./data/wcn.log

# 然后查看
tail -f ./data/wcn.log

# 或 systemd
journalctl -u wcn-api -f`}
      </pre>
      <div className="mt-4 text-ink-subtle text-xs">
        Tick 5 将提供 WebSocket 实时日志流 + level 过滤 + 虚拟列表.
      </div>
    </SpotlightCard>
  );
}
