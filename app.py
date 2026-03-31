import streamlit as st
from pathlib import Path

# ====================== 1. 页面配置 ======================
st.set_page_config(
    page_title="CSV数据可视化工具",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# ====================== 2. 唯一安全CSS：只隐藏Deploy，不动任何布局 ======================
st.markdown("""
<style>
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    header[data-testid="stHeader"]::before {
        content: "📊数据可视化分析";
        color: #000000;
        font-size: 40px;
        font-weight: 600;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        z-index: 999;
    }
    .stAppViewContainer {
        top: 0px !important;
        background: #f0f2f6 !important;
    }
    .stAppViewContainer {
    top: 0 !important;
    background: #f0f2f6 !important;
    }
    div[data-testid="stSidebarCollapsedControl"] button {
        color: black !important;
        fill: black !important;
    }
</style>
""", unsafe_allow_html=True)

# ====================== 3. 你的侧边栏（完全正常） ======================
with st.sidebar:
    st.header("功能选择")
    page = st.radio(
        "功能",
        ["单一数据分析", "数据分析", "文件处理"],
        key="page_select"
    )

# ====================== 4. 你的HTML代码（完全不变） ======================
html_file = Path(__file__).parent / "csv_visualization_with_data.html"
if html_file.exists():
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_content = '''
    <style>
        .html-wrapper {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background-color: #f0f2f6 !important;
        }
    </style>
    <div class="html-wrapper">''' + html_content + '''</div>'''

    st.components.v1.html(html_content, height=1000, scrolling=True, width="100%")
else:
    st.error("HTML文件未找到，请检查文件路径！")