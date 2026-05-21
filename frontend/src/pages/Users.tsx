import { useUsers } from "@/api/hooks";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { CheckCircle2 } from "lucide-react";

export default function Users() {
  const { data, isLoading } = useUsers(100);

  if (isLoading) return <div className="text-ink-subtle">加载用户...</div>;
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-20 text-ink-subtle">
        暂无用户. 用 <code className="text-primary">wcn run -u &lt;uid&gt;</code> 抓一个看看.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {data.map((u) => (
        <SpotlightCard key={u.uid} className="p-4 flex flex-col gap-2">
          <div className="flex items-start gap-3">
            {u.avatar_hd ? (
              <img
                src={u.avatar_hd}
                alt={u.screen_name}
                className="w-12 h-12 rounded-full border border-hairline"
                onError={(e) => (e.currentTarget.style.display = "none")}
              />
            ) : (
              <div className="w-12 h-12 rounded-full bg-primary/20 grid place-items-center text-primary font-bold">
                {u.screen_name.charAt(0)}
              </div>
            )}
            <div className="flex flex-col flex-1 min-w-0">
              <div className="flex items-center gap-1">
                <span className="text-ink font-medium truncate">{u.screen_name}</span>
                {u.verified && <CheckCircle2 size={14} className="text-primary shrink-0" />}
              </div>
              <span className="text-ink-subtle text-xs font-mono">uid {u.uid}</span>
            </div>
          </div>
          {u.description && (
            <div className="text-ink-muted text-xs line-clamp-2">{u.description}</div>
          )}
          <div className="flex gap-4 text-xs text-ink-subtle mt-1 pt-2 border-t border-hairline">
            <span>微博 <span className="text-ink">{u.statuses_count}</span></span>
            <span>粉丝 <span className="text-ink">{u.followers_count}</span></span>
            <span>关注 <span className="text-ink">{u.follow_count}</span></span>
          </div>
        </SpotlightCard>
      ))}
    </div>
  );
}
