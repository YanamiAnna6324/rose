"""Streamlit 外壳：把 index.html 整页嵌进来，只为拿一条公网 https 链接。

动画本身是 `index.html` 里的纯 Canvas 2D，不依赖 Python，直接双击也能跑。
这里只做三件事：

1. 把 Streamlit 自带的头部、边距、滚动条、页脚徽标全部藏掉；
2. 让组件 iframe 铺满整个视口（页面内部用的是 position: fixed）；
3. 把 `?play=1` / `?still=1` 透传成页面认识的 hash。

部署方式和 zodiacxMBTI 一样：推到公开 GitHub 仓库 → Streamlit Community Cloud
绑定本文件 → 拿到 `https://xxx.streamlit.app` 链接。
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

PAGE = Path(__file__).with_name("index.html")

# Streamlit 各版本的 DOM 结构改过几轮，这里新旧选择器都写上，
# 少一个就会在某个版本上露出白边或者多一条滚动条。
CHROME_CSS = """
<style>
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="stSidebarCollapsedControl"],
  #MainMenu,
  footer,
  .viewerBadge_container__1QSob,
  .stAppDeployButton {
    display: none !important;
  }

  html, body,
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {
    background: #000 !important;
    overflow: hidden !important;
  }

  .block-container,
  [data-testid="stMainBlockContainer"],
  [data-testid="stAppViewBlockContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
  }

  [data-testid="stVerticalBlock"],
  [data-testid="stElementContainer"] {
    gap: 0 !important;
  }

  /* 组件 iframe 铺满视口。100dvh 放在后面，手机上地址栏收起时才不会露黑边。 */
  iframe {
    position: fixed !important;
    inset: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    border: 0 !important;
    z-index: 10 !important;
  }
</style>
"""


def _page_html(fragment: str) -> str:
    """读 index.html；需要时把 hash 先写进去。"""
    markup = PAGE.read_text(encoding="utf-8")
    if fragment:
        inject = '<script>window.__ROSE_HASH = "%s";</script>' % fragment
        markup = markup.replace("<body>", "<body>\n" + inject, 1)
    return markup


def _fragment_from_query() -> str:
    """?play=1 → "#play"，?still=1 → "#still"。默认空，走「点一下，花开」。"""
    params = st.query_params
    if params.get("still"):
        return "#still"
    if params.get("play"):
        return "#play"
    return ""


def main() -> None:
    st.set_page_config(
        page_title="七夕快乐",
        page_icon="🌹",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CHROME_CSS, unsafe_allow_html=True)
    components.html(_page_html(_fragment_from_query()), height=900, scrolling=False)


if __name__ == "__main__":
    main()
