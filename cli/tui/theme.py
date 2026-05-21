"""Linear DESIGN.md 暗色 → Textual CSS.

色板 (来自 voltagent-design/linear.app):
  canvas      #010102   (深黑)
  surface-1   #0f1011   (卡片)
  surface-2   #141516
  hairline    #23252a   (描边)
  ink         #f7f8f8   (主文字)
  ink-muted   #d0d6e0
  ink-subtle  #8a8f98
  primary     #5e6ad2   (雪青蓝, 唯一品牌色)
"""

# Textual 全局样式 (.tcss / DEFAULT_CSS)
TUI_CSS = """
Screen {
    background: #010102;
    color: #f7f8f8;
}

Header {
    background: #0f1011;
    color: #f7f8f8;
    border-bottom: solid #23252a;
}

Footer {
    background: #0f1011;
    color: #d0d6e0;
    border-top: solid #23252a;
}

Footer > .footer--key {
    background: #5e6ad2;
    color: #ffffff;
    text-style: bold;
}

#sidebar {
    width: 28;
    background: #0f1011;
    border-right: solid #23252a;
    padding: 1 2;
}

#sidebar-title {
    color: #5e6ad2;
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
}

#main-content {
    padding: 1 2;
}

MenuList {
    height: auto;
    border: none;
    background: transparent;
}

MenuList > .option-list--option {
    padding: 1 2;
    color: #d0d6e0;
}

MenuList > .option-list--option-highlighted {
    background: #5e6ad2 30%;
    color: #ffffff;
    text-style: bold;
}

MenuList:focus > .option-list--option-highlighted {
    background: #5e6ad2;
    color: #ffffff;
}

Static.card {
    background: #0f1011;
    border: solid #23252a;
    padding: 1 2;
    margin-bottom: 1;
}

Static.card-title {
    color: #5e6ad2;
    text-style: bold;
    margin-bottom: 1;
}

Static.muted {
    color: #8a8f98;
}

Input {
    background: #141516;
    color: #f7f8f8;
    border: solid #23252a;
}

Input:focus {
    border: solid #5e6ad2;
}

DataTable {
    background: #0f1011;
}

DataTable > .datatable--header {
    background: #141516;
    color: #5e6ad2;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #5e6ad2 30%;
}

ProgressBar > Bar > .bar--bar {
    color: #5e6ad2;
}

ProgressBar > Bar > .bar--complete {
    color: #27a644;
}
"""
