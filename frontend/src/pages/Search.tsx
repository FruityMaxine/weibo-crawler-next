import { useState } from "react";
import { useSearch } from "@/api/hooks";
import { SpotlightCard } from "@/components/reactbits/SpotlightCard";
import { Search as SearchIcon } from "lucide-react";

export default function Search() {
  const [q, setQ] = useState("");
  const [submitted, setSubmitted] = useState("");
  const { data, isLoading } = useSearch(submitted);

  return (
    <div className="flex flex-col gap-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(q.trim());
        }}
        className="flex gap-2"
      >
        <div className="flex-1 relative">
          <SearchIcon
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-subtle"
          />
          <input
            className="w-full bg-surface-2 border border-hairline rounded-md pl-9 pr-3 py-2.5 text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:border-primary"
            placeholder="FTS5 表达式: '编程' / '编程 AND Python' / 'Python OR Rust'"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <button
          type="submit"
          className="bg-primary text-white px-5 rounded-md text-sm font-medium hover:bg-primary-hover transition-colors"
        >
          搜索
        </button>
      </form>

      {submitted && (
        <div className="text-ink-subtle text-xs">
          query: <code className="text-primary">{submitted}</code>
          {data ? ` · ${data.count} 命中` : ""}
        </div>
      )}

      {isLoading && <div className="text-ink-subtle">搜索中...</div>}

      <div className="flex flex-col gap-3">
        {data?.hits.map((h) => (
          <SpotlightCard key={h.weibo_id} className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-ink-subtle text-xs font-mono">
                {h.weibo_id} · uid {h.uid} · score {h.score.toFixed(2)}
              </div>
              <span className="text-ink-subtle text-xs">
                {h.created_at ? new Date(h.created_at).toLocaleString() : ""}
              </span>
            </div>
            <div
              className="text-ink text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: h.snippet || h.text }}
            />
          </SpotlightCard>
        ))}
        {submitted && data?.count === 0 && (
          <div className="text-center py-12 text-ink-subtle">
            没找到匹配项. 试试更简短的关键词.
          </div>
        )}
      </div>
    </div>
  );
}
