import { Users, MessageSquare, ListChecks, Activity } from "lucide-react";
import { Aurora } from "@/components/reactbits/Aurora";
import { TypingText } from "@/components/reactbits/TypingText";
import { MagneticButton } from "@/components/reactbits/MagneticButton";
import { StatCard } from "@/components/StatCard";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { useWebSocket } from "@/hooks/useWebSocket";

export default function Dashboard() {
  const { tick, connected } = useWebSocket();
  const stats = tick?.stats ?? { users: 0, weibos: 0, tasks: 0 };
  const recent = tick?.recent_tasks ?? [];

  return (
    <div className="flex flex-col gap-6">
      <section className="relative overflow-hidden rounded-xl border border-hairline bg-surface p-8">
        <Aurora />
        <div className="relative">
          <div className="text-ink-subtle text-xs uppercase tracking-wider mb-2">
            weibo-crawler-next · 现代化微博数据采集平台
          </div>
          <h2 className="text-4xl font-semibold tracking-tight2x text-ink">
            <TypingText text="为研究者打造的微博数据中台." speed={28} />
          </h2>
          <p className="mt-3 text-ink-muted max-w-xl">
            插件化导出 · 高阶风控 · CLI 与 WebUI 双模式 · 完整可发版的工具链.
          </p>
          <div className="mt-5 flex gap-3">
            <MagneticButton variant="primary">新建采集任务</MagneticButton>
            <MagneticButton variant="ghost">查看 API 文档</MagneticButton>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="已抓用户" value={stats.users} icon={<Users size={18} />} />
        <StatCard label="已抓微博" value={stats.weibos} icon={<MessageSquare size={18} />} />
        <StatCard label="任务总数" value={stats.tasks} icon={<ListChecks size={18} />} />
        <StatCard
          label="WS 状态"
          value={connected ? 1 : 0}
          icon={<Activity size={18} />}
          trend={connected ? "实时数据流" : "等待重连"}
        />
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SpotlightCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-ink font-semibold">最近任务</h3>
            <span className="text-ink-subtle text-xs">实时刷新</span>
          </div>
          <div className="flex flex-col gap-2">
            {recent.length === 0 && (
              <div className="text-ink-subtle text-sm py-8 text-center">
                暂无任务. 启动 <code className="text-primary">wcn run -u &lt;uid&gt;</code> 开始.
              </div>
            )}
            {recent.map((t) => (
              <div
                key={t.id}
                className="flex items-center justify-between border border-hairline rounded-md px-3 py-2 bg-surface-2"
              >
                <div className="flex flex-col">
                  <span className="text-ink text-sm">#{t.id} {t.name}</span>
                  <span className="text-ink-subtle text-xs">
                    {t.status} · 已抓 {t.total_fetched}
                  </span>
                </div>
                <div className="font-mono text-primary text-sm">{t.progress}%</div>
              </div>
            ))}
          </div>
        </SpotlightCard>

        <SpotlightCard className="p-5">
          <h3 className="text-ink font-semibold mb-4">系统提示</h3>
          <ul className="space-y-2 text-sm text-ink-muted">
            <li>• 后端绑定 <code className="text-primary">127.0.0.1:28800</code> · 前端 dev :5173</li>
            <li>• SQLite + FTS5 全文索引已就绪</li>
            <li>• WebSocket 每 3 秒推送一次仪表盘数据</li>
            <li>• 6 种导出器: CSV / JSON / SQLite / MySQL / MongoDB / Webhook</li>
            <li>• Tick 5 即将加入: Cookie/Proxy 池 + Telegram/Discord 通知</li>
          </ul>
        </SpotlightCard>
      </section>
    </div>
  );
}
