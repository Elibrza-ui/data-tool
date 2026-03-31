import streamlit as st
from pathlib import Path

# ====================== 1. 页面配置 ======================
st.set_page_config(
    page_title="CSV数据可视化工具",
    layout="wide",
    initial_sidebar_state="collapsed",
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
        white-space: nowrap; 
    }
    .stAppViewContainer {
        top: 0px !important;
        background: #f0f2f6 !important;
    }
    .stAppViewContainer {
        top: 0 !important;
        background: #f0f2f6 !important;
    }
        div[data-testid="stSidebarCollapsedControl"] button svg {
        fill: #000000 !important;
    }
    /* 自定义侧边栏宽度 */
    section[data-testid="stSidebar"][aria-expanded="true"]{
        width: 160px !important;       /* 展开时的宽度 */
    }
</style>
""", unsafe_allow_html=True)

# ====================== 侧边栏 ======================
with st.sidebar:
    st.header("功能选择")
    page = st.radio(
        "",
        ["单一数据分析", "数据分析", "文件处理"],
        key="page_select"
    )

if page == "单一数据分析":
    # 加载CSV可视化HTML
    # ====================== HTML代码 ======================
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

elif page == "数据分析":
    st.markdown("<div style='text-align:center; padding:50px;'><h2 style='color:black;'>📈 数据分析页面（开发中）</h2></div>", unsafe_allow_html=True)

elif page == "文件处理":
    try:
        from file_processor import render_file_processor_page
        render_file_processor_page()
    except Exception as e:
        st.error(f"❌ 加载文件处理模块失败: {str(e)}")
        st.info("请检查 file_processor.py 文件是否存在")
