"""微博 API endpoint 常量 — 集中管理避免散落.

来源参照: dataabc/weibo-crawler 项目对 m.weibo.cn API 的调用方式.
本项目不抄代码, 仅复用 API URL 知识.
"""

API_BASE_M = "https://m.weibo.cn"
API_BASE_WEIBO_COM = "https://weibo.com"

# 用户信息容器接口 (返回 user_info + tabs)
USER_INFO = f"{API_BASE_M}/api/container/getIndex"
# 用户微博列表接口 (containerid=107603{uid})
USER_WEIBO_LIST = f"{API_BASE_M}/api/container/getIndex"
# 热门评论 (一级)
WEIBO_COMMENTS_HOTFLOW = f"{API_BASE_M}/comments/hotflow"
# 转发列表
WEIBO_REPOST_TIMELINE = f"{API_BASE_M}/api/statuses/repostTimeline"
# 关键词搜索 (需 cookie)
WEIBO_SEARCH = f"{API_BASE_M}/api/container/getIndex"
# 单条微博详情 (长文本)
WEIBO_DETAIL = f"{API_BASE_M}/statuses/show"
# 长文章
WEIBO_LONGTEXT = f"{API_BASE_M}/statuses/extend"


def user_container_id(uid: int | str) -> str:
    """微博的 containerid 规则: 107603 + uid."""
    return f"107603{uid}"


def search_container_id(q: str, kind: str = "1") -> str:
    """关键词搜索的 containerid: 100103type=1&q={q}."""
    return f"100103type={kind}&q={q}"
