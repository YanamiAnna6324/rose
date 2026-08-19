"""Streamlit 外壳：只为拿一条公网 https 链接，好在手机上试。

四个版本都是纯前端单页，不依赖 Python。这里只做四件事：
把 Streamlit 自己的头/边距/滚动条藏掉、让 iframe 铺满视口、
顶上放一个切版本的选择器、把 ?play / ?still 透传成页面认识的 hash。

部署：推到公开 GitHub 仓库 → share.streamlit.io 绑定本文件 → 拿到
https://xxx.streamlit.app。不需要任何 Secrets。
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent

# 顺序就是选择器上的顺序，第一个是默认
VERSIONS = {
    "结合版": ("index_mix.html", "粒子的圆球形 + 照片的真实配色，可拖动旋转"),
    "照片版": ("index_photo.html", "照片抠图后充气成立体，可拖动旋转"),
    "粒子版": ("index.html", "手工建模的粒子花束，自转 + 呼吸运镜"),
    "泼溅版": ("index_splat.html", "TripoSplat 生成的 3D 高斯泼溅，WebGL 渲染"),
}

# 选择器占的高度，iframe 用 100vh 减掉它。
# 不减的话页面会多出一条滚动条，手机上花束会被顶下去半截。
BAR_PX = 74

CHROME_CSS = """
<style>
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="stSidebarCollapsedControl"],
  #MainMenu, footer, .stAppDeployButton {
    display: none !important;
  }

  html, body, .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {
    background: #000 !important;
    overflow: hidden !important;
  }

  .block-container,
  [data-testid="stMainBlockContainer"],
  [data-testid="stAppViewBlockContainer"] {
    padding: 6px 8px 0 8px !important;
    margin: 0 !important;
    max-width: 100% !important;
  }

  [data-testid="stVerticalBlock"],
  [data-testid="stElementContainer"] { gap: 0 !important; }

  /* 选择器压扁一点，手机上别占太高 */
  [data-testid="stRadio"] > label { display: none !important; }
  [data-testid="stRadio"] div[role="radiogroup"] {
    gap: 4px !important;
    justify-content: center;
    flex-wrap: nowrap;
  }
  [data-testid="stRadio"] label p { font-size: 13px !important; }

  /* 组件 iframe 铺满剩下的视口。100dvh 放后面，手机地址栏收起时才不露黑边 */
  iframe {
    width: 100% !important;
    height: calc(100vh - __BAR__px) !important;
    height: calc(100dvh - __BAR__px) !important;
    border: 0 !important;
    display: block;
  }
</style>
""".replace("__BAR__", str(BAR_PX))


# 泼溅版是唯一要外部加载资源的（static/rose.splat 8MB + static/splat-render.js）。
# srcdoc iframe 的 location.href 是 "about:srcdoc"，相对路径一律解析不到，
# 所以得把基址喂进去。iframe 和外层同源，parent.location 拿得到。
BOOT = """<script>
window.__ROSE_HASH = "{frag}";
window.__ROSE_BASE = (function () {{
  try {{ return parent.location.origin + "/app/"; }} catch (e) {{ return ""; }}
}})();
</script>"""

# 外部 script 的相对路径同样解析不到，换成用绝对地址重新写一遍。
# 这里必须用 document.write：splat-render.js 要在页面自己那段脚本之前
# 同步执行完，改成 appendChild 异步加载会打乱顺序。
SPLAT_TAG = '<script src="static/splat-render.js"></script>'
SPLAT_SHIM = (
    "<script>document.write('<scr' + 'ipt src=\"' + window.__ROSE_BASE"
    " + 'static/splat-render.js\"></scr' + 'ipt>');</script>"
)


def page_html(name: str, fragment: str) -> str:
    markup = (HERE / name).read_text(encoding="utf-8")
    boot = BOOT.format(frag=fragment)
    markup = markup.replace(SPLAT_TAG, SPLAT_SHIM, 1)
    # 有 <body> 就插在它后面，没有就插到最前面（这几个页面写法不统一）
    if "<body>" in markup:
        markup = markup.replace("<body>", "<body>\n" + boot, 1)
    else:
        markup = boot + "\n" + markup
    return markup


def fragment_from_query() -> str:
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

    names = list(VERSIONS)
    # ?v=结合版 之类可以直接指定，方便把某一版单独发出去
    want = st.query_params.get("v")
    index = names.index(want) if want in names else 0

    choice = st.radio("版本", names, index=index, horizontal=True,
                      label_visibility="collapsed")
    fname, blurb = VERSIONS[choice]
    st.caption(blurb)

    if not (HERE / fname).exists():
        st.error("找不到 %s" % fname)
        return

    components.html(page_html(fname, fragment_from_query()), height=900,
                    scrolling=False)


if __name__ == "__main__":
    main()
