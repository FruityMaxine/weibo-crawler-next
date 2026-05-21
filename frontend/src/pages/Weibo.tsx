import { useState } from "react";
import { useWeibo } from "@/api/hooks";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { Heart, MessageCircle, Share2, Repeat2 } from "lucide-react";

export default function Weibo() {
  const [uidFilter, setUidFilter] = useState<string>("");
  const uid = uidFilter ? Number(uidFilter) : undefined;
  const { data, isLoading } = useWeibo(uid, 100);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <input
          className="bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary w-64"
          placeholder="按 UID 过滤 (留空显示全部)"
          value={uidFilter}
          onChange={(e) => setUidFilter(e.target.value.replace(/\D/g, ""))}
        />
        {data && <span className="text-ink-subtle text-xs">共 {data.length} 条</span>}
      </div>

      {isLoading && <div className="text-ink-subtle">加载微博...</div>}

      <div className="flex flex-col gap-3">
        {data?.map((w) => (
          <SpotlightCard key={w.weibo_id} className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-ink-subtle text-xs font-mono">
                {w.weibo_id} · uid {w.uid}
              </div>
              <div className="flex items-center gap-1.5 text-xs">
                {w.is_retweet && <Repeat2 size={12} className="text-ink-subtle" />}
                <span className="text-ink-subtle">{w.source ?? ""}</span>
                <span className="text-ink-subtle">
                  {w.created_at ? new Date(w.created_at).toLocaleString() : ""}
                </span>
              </div>
            </div>
            <div className="text-ink leading-relaxed whitespace-pre-wrap break-words">
              {w.text}
            </div>
            {w.pic_urls.length > 0 && (
              <div className="mt-3 flex gap-2 flex-wrap">
                {w.pic_urls.slice(0, 4).map((u) => (
                  <img
                    key={u}
                    src={u}
                    alt=""
                    className="h-20 w-20 rounded border border-hairline object-cover"
                    onError={(e) => (e.currentTarget.style.display = "none")}
                    referrerPolicy="no-referrer"
                  />
                ))}
              </div>
            )}
            <div className="flex gap-5 mt-3 pt-3 border-t border-hairline text-xs text-ink-subtle">
              <span className="flex items-center gap-1"><Heart size={12} /> {w.attitudes_count}</span>
              <span className="flex items-center gap-1"><MessageCircle size={12} /> {w.comments_count}</span>
              <span className="flex items-center gap-1"><Share2 size={12} /> {w.reposts_count}</span>
            </div>
          </SpotlightCard>
        ))}
        {data?.length === 0 && (
          <div className="text-center py-20 text-ink-subtle">
            暂无微博. 用 <code className="text-primary">wcn run -u &lt;uid&gt;</code> 抓一些.
          </div>
        )}
      </div>
    </div>
  );
}
