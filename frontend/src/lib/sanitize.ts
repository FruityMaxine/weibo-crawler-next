/**
 * 前端 sanitize 工具 — 防 XSS.
 *
 * v0.7.0.0 修 reviewer 报告的 Search.tsx dangerouslySetInnerHTML XSS.
 *
 * 用法:
 *   import { sanitizeHtml, sanitizeText } from "@/lib/sanitize";
 *   <div dangerouslySetInnerHTML={{ __html: sanitizeHtml(userInput) }} />
 *
 * 实现说明:
 *   生产用 DOMPurify, 但为了零依赖也支持 fallback (仅在 DOMPurify 不可用时).
 *   FTS5 snippet 唯一允许 <mark> 标签 (高亮关键词).
 */

// 只允许的标签 (FTS5 snippet 需要 <mark>)
const ALLOWED_TAGS = new Set(["mark", "b", "strong", "em", "i"]);

// 简易 fallback: 仅保留白名单标签
function fallbackSanitize(html: string): string {
  if (!html) return "";
  // 先剥掉所有 <script>/<style>/<iframe>/事件属性
  let s = html
    .replace(/<script\b[\s\S]*?<\/script\s*>/gi, "")
    .replace(/<style\b[\s\S]*?<\/style\s*>/gi, "")
    .replace(/<iframe\b[\s\S]*?<\/iframe\s*>/gi, "")
    .replace(/<object\b[\s\S]*?<\/object\s*>/gi, "")
    .replace(/<embed\b[\s\S]*?<\/embed\s*>/gi, "");
  // 剥 on* 事件属性
  s = s.replace(/\son\w+\s*=\s*"[^"]*"/gi, "");
  s = s.replace(/\son\w+\s*=\s*'[^']*'/gi, "");
  s = s.replace(/\son\w+\s*=\s*[^\s>]+/gi, "");
  // 剥 javascript: 协议
  s = s.replace(/javascript:/gi, "");
  // 剥所有不在白名单的标签
  return s.replace(/<\/?(\w+)\b[^>]*>/g, (match, tag: string) => {
    if (ALLOWED_TAGS.has(tag.toLowerCase())) return match;
    return "";
  });
}

/**
 * Sanitize HTML 字符串 — 优先 DOMPurify, fallback 内置白名单实现.
 *
 * 适用: FTS5 snippet 中带 <mark> 高亮的微博正文.
 */
export function sanitizeHtml(html: string | null | undefined): string {
  if (!html) return "";
  // 优先尝试 DOMPurify (如安装了)
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const dompurify = (globalThis as any).DOMPurify;
    if (dompurify && typeof dompurify.sanitize === "function") {
      return dompurify.sanitize(html, {
        ALLOWED_TAGS: Array.from(ALLOWED_TAGS),
        ALLOWED_ATTR: [],
      });
    }
  } catch {
    /* ignore, fall through to fallback */
  }
  return fallbackSanitize(html);
}

/**
 * 完全剥离 HTML, 返回纯文本.
 *
 * 适用: 显示用户提交的微博正文且不需任何格式.
 */
export function sanitizeText(s: string | null | undefined): string {
  if (!s) return "";
  return s.replace(/<\/?[^>]+>/g, "").replace(/&\w+;/g, " ").trim();
}
