import streamlit as st
from pathlib import Path

# ====================== 1. 页面配置（必须第一行执行） ======================
st.set_page_config(
    page_title="CSV数据可视化工具",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# ====================== 2. 核心CSS ======================
st.markdown("""
<style>
    /* 完全隐藏Streamlit原生顶部栏 */
    [data-testid="stHeader"] {
        display: none !important;
    }

    /* 隐藏原生侧边栏收起按钮 */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    /* 自定义顶部黑色固定标题栏（永远不动） */
    .custom-header {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 60px !important;
        background-color: #1e293b !important;
        z-index: 1000000 !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 20px !important;
    }

    /* 标题样式：在黑栏内完整显示，白色，不被遮挡 */
    .custom-header h1 {
        color: white !important;
        font-size: 1.8rem !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 60px !important;
        white-space: nowrap !important;
    }

    /* 侧边栏：从标题栏下方开始，固定不动 */
    [data-testid="stSidebar"] {
        top: 60px !important;
        height: calc(100vh - 60px) !important;
        position: fixed !important;
        z-index: 9998 !important;
        background-color: #1e293b !important;
        width: 180px !important;
        min-width: 180px !important;
    }

    /* 主内容区：从标题栏下方开始，为侧边栏留出空间 */
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stAppViewContainer"] > .main .block-container,
    section[data-testid="stMain"] {
        margin-top: 60px !important;
        margin-left: 180px !important;
        max-width: calc(100vw - 180px) !important;
        padding: 1rem !important;
        background-color: #f0f2f6 !important;
    }

    /* 侧边栏文字样式：白色、不换行 */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] label {
        color: white !important;
        white-space: nowrap !important;
        font-size: 1.1rem !important;
    }

    /* 只针对主容器和核心元素去除黑边，保留组件样式 */
    [data-testid="stAppViewContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ====================== 3. 自定义标题 ======================
st.markdown("""
<div class="custom-header">
    <h1>📊 CSV数据可视化工具</h1>
</div>
""", unsafe_allow_html=True)

# ====================== 4. 侧边栏功能选择 ======================
with st.sidebar:
    st.header("功能选择")
    page = st.radio(
        "功能",
        ["单一数据分析", "数据分析", "文件处理"],
        key="page_select"
    )

# ====================== 5. 页面内容逻辑 ======================
if page == "单一数据分析":
    # 加载你的CSV可视化HTML
    html_file = Path(__file__).parent / "csv_visualization_with_data.html"
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # 安全去黑边（不影响Streamlit组件）
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
    st.markdown("<div style='text-align:center; padding:50px;'><h2>📈 数据分析页面（开发中）</h2></div>", unsafe_allow_html=True)

elif page == "文件处理":
    try:
        from file_processor import render_file_processor_page
        render_file_processor_page()
    except Exception as e:
        st.error(f"❌ 加载文件处理模块失败: {str(e)}")
        st.info("请检查 file_processor.py 文件是否存在")
