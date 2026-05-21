import { useState } from "react";
import { useTasks, useCreateTask } from "@/api/hooks";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { MagneticButton } from "@/components/reactbits/MagneticButton";
import { Plus } from "lucide-react";

export default function Tasks() {
  const { data, isLoading, error } = useTasks();
  const create = useCreateTask();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", uid: "", max_count: 50 });

  async function submit() {
    if (!form.name.trim() || !form.uid.trim()) return;
    try {
      await create.mutateAsync({
        name: form.name,
        uid: Number(form.uid),
        max_count: form.max_count,
      });
      setShowForm(false);
      setForm({ name: "", uid: "", max_count: 50 });
    } catch (e) {
      alert("创建失败: " + String(e));
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <p className="text-ink-muted text-sm">
          采集任务以异步后台运行, 进度通过 WS 实时推送.
        </p>
        <MagneticButton
          onClick={() => setShowForm(true)}
          className="inline-flex items-center gap-1.5"
        >
          <Plus size={14} /> 新建任务
        </MagneticButton>
      </div>

      {showForm && (
        <SpotlightCard className="p-5 space-y-3">
          <h3 className="font-semibold text-ink">新建采集任务</h3>
          <input
            className="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary"
            placeholder="任务名称, e.g. 周末抓 X 用户"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
          <input
            className="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary"
            placeholder="微博 UID, e.g. 1669879400"
            value={form.uid}
            onChange={(e) => setForm({ ...form, uid: e.target.value })}
          />
          <input
            type="number"
            className="w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary"
            placeholder="最大条数"
            value={form.max_count}
            onChange={(e) => setForm({ ...form, max_count: Number(e.target.value) })}
          />
          <div className="flex gap-2">
            <MagneticButton onClick={submit}>创建并启动</MagneticButton>
            <MagneticButton variant="ghost" onClick={() => setShowForm(false)}>
              取消
            </MagneticButton>
          </div>
        </SpotlightCard>
      )}

      {isLoading && <div className="text-ink-subtle text-sm">加载任务...</div>}
      {error && <div className="text-danger text-sm">加载失败: {String(error)}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {data?.map((t) => (
          <SpotlightCard key={t.id} className="p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <div className="text-ink font-medium">#{t.id} {t.name}</div>
                <div className="text-ink-subtle text-xs">
                  uid {t.uid ?? "—"} · 创建 {new Date(t.created_at).toLocaleString()}
                </div>
              </div>
              <span
                className={`text-xs px-2 py-0.5 rounded font-mono ${
                  t.status === "success" ? "bg-success/15 text-success"
                    : t.status === "failed" ? "bg-danger/15 text-danger"
                    : t.status === "running" ? "bg-primary/15 text-primary animate-pulse-glow"
                    : "bg-surface-2 text-ink-subtle"
                }`}
              >
                {t.status}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2 bg-surface-2 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all duration-500"
                  style={{ width: `${t.progress}%` }}
                />
              </div>
              <span className="font-mono text-xs text-ink-muted w-10">{t.progress}%</span>
            </div>
            <div className="text-ink-subtle text-xs mt-2">已抓 {t.total_fetched} 条</div>
            {t.error && (
              <div className="mt-2 text-danger text-xs font-mono break-all">{t.error.slice(0, 200)}</div>
            )}
          </SpotlightCard>
        ))}
        {data?.length === 0 && (
          <div className="col-span-full text-center py-12 text-ink-subtle">
            暂无任务. 点击右上 [新建任务] 创建第一个.
          </div>
        )}
      </div>
    </div>
  );
}
