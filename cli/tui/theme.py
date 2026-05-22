"""Linear DESIGN.md 暗色基底 + 七彩状态色 → Textual CSS.

色板 (基础 Linear 暗色):
  canvas      #010102   深黑
  surface-1   #0f1011   卡片
  surface-2   #141516   嵌套卡片
  hairline    #23252a   描边
  ink         #f7f8f8   主文字
  ink-muted   #d0d6e0
  ink-subtle  #8a8f98
  primary     #5e6ad2   雪青蓝 (品牌色)

七彩功能色 (按用户明示 "七彩" 风格):
  success     #27a644   绿  成功 / 完成 / 已抓
  warning     #d9a300   黄  暂停 / 限频
  danger      #d65555   红  失败 / 错误
  info        #4ec3ff   青  信息 / 链接
  accent2     #ff7eb6   粉  搜索高亮 / 转发标记
  accent3     #b88aff   紫  原创 / Live Photo
  accent4     #ffaa3e   橙  进度 / 警示
"""

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
    width: 32;
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

#sidebar-version {
    color: #8a8f98;
    text-align: center;
    margin-bottom: 1;
}

#main-content {
    padding: 1 2;
}

MenuList, OptionList {
    height: auto;
    border: none;
    background: transparent;
}

MenuList > .option-list--option,
OptionList > .option-list--option {
    padding: 1 2;
    color: #d0d6e0;
}

MenuList > .option-list--option-highlighted,
OptionList > .option-list--option-highlighted {
    background: #5e6ad2 30%;
    color: #ffffff;
    text-style: bold;
}

MenuList:focus > .option-list--option-highlighted,
OptionList:focus > .option-list--option-highlighted {
    background: #5e6ad2;
    color: #ffffff;
    text-style: bold;
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

Static.muted { color: #8a8f98; }
Static.success { color: #27a644; }
Static.warning { color: #d9a300; }
Static.danger  { color: #d65555; }
Static.info    { color: #4ec3ff; }
Static.accent2 { color: #ff7eb6; }
Static.accent3 { color: #b88aff; }
Static.accent4 { color: #ffaa3e; }

Label {
    color: #d0d6e0;
    padding: 1 0 0 0;
}

Input {
    background: #141516;
    color: #f7f8f8;
    border: solid #23252a;
    padding: 0 1;
}

Input:focus {
    border: solid #5e6ad2;
}

Input.-invalid {
    border: solid #d65555;
}

Button {
    margin: 1 1 0 0;
}

Button.-primary {
    background: #5e6ad2;
    color: #ffffff;
}

Button.-primary:hover {
    background: #828fff;
}

Button.-success {
    background: #27a644;
    color: #ffffff;
}

Button.-danger {
    background: #d65555;
    color: #ffffff;
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

ProgressBar > Bar > .bar--indeterminate {
    color: #ffaa3e;
}

RichLog {
    background: #0a0a0c;
    border: solid #23252a;
    padding: 0 1;
}

Select {
    background: #141516;
    color: #f7f8f8;
    border: solid #23252a;
}

Select:focus {
    border: solid #5e6ad2;
}
"""
