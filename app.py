import streamlit as st
import pandas as pd
from data_processor import DataProcessor
import plotly.express as px
import plotly.graph_objects as go
import os
import streamlit.components.v1 as components

# 页面配置
st.set_page_config(
    page_title="数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """主函数"""

    # 侧边栏配置
    st.sidebar.header("⚙️ 配置")

    # 选择显示模式
    mode = st.sidebar.radio(
        "选择显示模式",
        ["Streamlit 原生界面", "自定义 HTML 页面"],
        help="选择使用 Streamlit 界面或你的自定义 HTML 页面"
    )

    # ========== 模式1: Streamlit 原生界面 ==========
    if mode == "Streamlit 原生界面":
        # 标题
        st.markdown('<h1 class="main-title">📊 数据分析平台</h1>', unsafe_allow_html=True)
        st.markdown("---")

        # 数据路径输入
        data_path = st.sidebar.text_input(
            "数据文件夹路径",
            value="./data",
            help="包含12个子文件夹的根目录"
        )

        # 初始化session state
        if 'processor' not in st.session_state:
            st.session_state.processor = None
        if 'current_df' not in st.session_state:
            st.session_state.current_df = None

        # 加载数据按钮
        if st.sidebar.button("🔄 加载数据", use_container_width=True):
            with st.spinner("正在加载数据..."):
                processor = DataProcessor(data_path)
                df = processor.load_all_data()

                if not df.empty:
                    st.session_state.processor = processor
                    st.session_state.current_df = df
                    st.sidebar.success("✅ 数据加载成功!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ 数据加载失败!")

        # 如果没有数据，显示提示
        if st.session_state.current_df is None:
            st.info("👈 请在左侧配置数据路径并点击'加载数据'按钮")
            return

        processor = st.session_state.processor
        df = st.session_state.current_df

        # ========== 数据概览 ==========
        st.header("📈 数据概览")

        # 统计信息
        summary = processor.get_summary_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("总行数", f"{summary['total_rows']:,}")
        with col2:
            st.metric("总列数", summary['total_columns'])
        with col3:
            st.metric("文件夹数", summary['folder_count'])
        with col4:
            st.metric("内存占用", f"{summary['memory_usage_mb']:.2f} MB")

        # 数据预览
        st.subheader("数据预览")
        with st.expander("查看原始数据", expanded=False):
            st.dataframe(df.head(100), use_container_width=True)

        # ========== 数据筛选 ==========
        st.header("🔍 数据筛选")

        # 按文件夹筛选
        if 'source_folder' in df.columns:
            all_folders = sorted(df['source_folder'].unique())
            selected_folders = st.multiselect(
                "选择文件夹",
                all_folders,
                default=all_folders
            )

            if selected_folders:
                df = df[df['source_folder'].isin(selected_folders)]

        # 按列筛选
        all_columns = df.columns.tolist()
        numeric_columns = processor.get_numeric_columns()

        if numeric_columns:
            st.subheader("数值筛选")

            col_a, col_b = st.columns(2)

            with col_a:
                filter_column = st.selectbox("选择列", numeric_columns)

            with col_b:
                col_min, col_max = st.columns(2)
                min_val = col_min.number_input("最小值", value=float(df[filter_column].min()))
                max_val = col_max.number_input("最大值", value=float(df[filter_column].max()))

            if st.button("应用数值筛选"):
                df = df[(df[filter_column] >= min_val) & (df[filter_column] <= max_val)]
                st.success(f"✅ 筛选后剩余 {len(df):,} 条数据")

        # ========== 差分计算 ==========
        st.header("📊 差分计算")

        with st.expander("计算差分"):
            diff_column = st.selectbox("选择要计算差分的列", numeric_columns)

            if st.button("计算差分"):
                df = processor.calculate_diff(diff_column)
                st.success(f"✅ 已添加列: {diff_column}_diff")

        # ========== 数据可视化 ==========
        st.header("📉 数据可视化")

        # 图表类型选择
        chart_type = st.selectbox(
            "选择图表类型",
            ["折线图", "柱状图", "散点图", "直方图"]
        )

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if chart_type in ["折线图", "柱状图"]:
            x_col = st.selectbox("X轴", df.columns.tolist())
            y_col = st.selectbox("Y轴", numeric_cols)

            if chart_type == "折线图":
                fig = px.line(df, x=x_col, y=y_col, color='source_folder' if 'source_folder' in df.columns else None)
            else:
                fig = px.bar(df, x=x_col, y=y_col, color='source_folder' if 'source_folder' in df.columns else None)

            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "散点图":
            x_col = st.selectbox("X轴", numeric_cols)
            y_col = st.selectbox("Y轴", [c for c in numeric_cols if c != x_col])
            color_col = st.selectbox("颜色分组", ["无"] + df.columns.tolist())

            fig = px.scatter(df, x=x_col, y=y_col, color=color_col if color_col != "无" else None)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "直方图":
            x_col = st.selectbox("选择列", numeric_cols)
            fig = px.histogram(df, x=x_col, nbins=50)
            st.plotly_chart(fig, use_container_width=True)

        # ========== 数据导出 ==========
        st.header("💾 数据导出")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("导出为 CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="下载 CSV",
                    data=csv,
                    file_name=f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("导出筛选后数据"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="下载筛选后数据",
                    data=csv,
                    file_name=f"filtered_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        # 页脚
        st.markdown("---")
        st.markdown("<center><small>💡 提示: 调整筛选条件后数据会自动更新</small></center>", unsafe_allow_html=True)

    # ========== 模式2: 自定义 HTML 页面 ==========
    else:
        st.markdown('<h1 class="main-title">📊 数据分析平台 (HTML模式)</h1>', unsafe_allow_html=True)
        st.markdown("---")

        # HTML 文件路径
        html_file_path = st.sidebar.text_input(
            "HTML 文件路径",
            value="./csv_visualization_with_data.html",
            help="你的自定义 HTML 文件路径"
        )

        # 检查文件是否存在
        if os.path.exists(html_file_path):
            st.sidebar.success(f"✅ 找到文件: {html_file_path}")

            # 读取并显示 HTML
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 使用 Streamlit 的 html 组件显示
            components.html(html_content, height=800, scrolling=True)

            st.info("💡 这是你自定义的 HTML 页面,嵌入在 Streamlit 中显示")
        else:
            st.error(f"❌ 未找到文件: {html_file_path}")
            st.info("📝 请确保:")
            st.info("1. HTML 文件在项目根目录下")
            st.info("2. 文件名正确(区分大小写)")
            st.info("3. 路径填写正确")


if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
from data_processor import DataProcessor
import plotly.express as px
import plotly.graph_objects as go
import os
import streamlit.components.v1 as components

# 页面配置
st.set_page_config(
    page_title="数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """主函数"""

    # 侧边栏配置
    st.sidebar.header("⚙️ 配置")

    # 选择显示模式
    mode = st.sidebar.radio(
        "选择显示模式",
        ["Streamlit 原生界面", "自定义 HTML 页面"],
        help="选择使用 Streamlit 界面或你的自定义 HTML 页面"
    )

    # ========== 模式1: Streamlit 原生界面 ==========
    if mode == "Streamlit 原生界面":
        # 标题
        st.markdown('<h1 class="main-title">📊 数据分析平台</h1>', unsafe_allow_html=True)
        st.markdown("---")

        # 数据路径输入
        data_path = st.sidebar.text_input(
            "数据文件夹路径",
            value="./data",
            help="包含12个子文件夹的根目录"
        )

        # 初始化session state
        if 'processor' not in st.session_state:
            st.session_state.processor = None
        if 'current_df' not in st.session_state:
            st.session_state.current_df = None

        # 加载数据按钮
        if st.sidebar.button("🔄 加载数据", use_container_width=True):
            with st.spinner("正在加载数据..."):
                processor = DataProcessor(data_path)
                df = processor.load_all_data()

                if not df.empty:
                    st.session_state.processor = processor
                    st.session_state.current_df = df
                    st.sidebar.success("✅ 数据加载成功!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ 数据加载失败!")

        # 如果没有数据，显示提示
        if st.session_state.current_df is None:
            st.info("👈 请在左侧配置数据路径并点击'加载数据'按钮")
            return

        processor = st.session_state.processor
        df = st.session_state.current_df

        # ========== 数据概览 ==========
        st.header("📈 数据概览")

        # 统计信息
        summary = processor.get_summary_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("总行数", f"{summary['total_rows']:,}")
        with col2:
            st.metric("总列数", summary['total_columns'])
        with col3:
            st.metric("文件夹数", summary['folder_count'])
        with col4:
            st.metric("内存占用", f"{summary['memory_usage_mb']:.2f} MB")

        # 数据预览
        st.subheader("数据预览")
        with st.expander("查看原始数据", expanded=False):
            st.dataframe(df.head(100), use_container_width=True)

        # ========== 数据筛选 ==========
        st.header("🔍 数据筛选")

        # 按文件夹筛选
        if 'source_folder' in df.columns:
            all_folders = sorted(df['source_folder'].unique())
            selected_folders = st.multiselect(
                "选择文件夹",
                all_folders,
                default=all_folders
            )

            if selected_folders:
                df = df[df['source_folder'].isin(selected_folders)]

        # 按列筛选
        all_columns = df.columns.tolist()
        numeric_columns = processor.get_numeric_columns()

        if numeric_columns:
            st.subheader("数值筛选")

            col_a, col_b = st.columns(2)

            with col_a:
                filter_column = st.selectbox("选择列", numeric_columns)

            with col_b:
                col_min, col_max = st.columns(2)
                min_val = col_min.number_input("最小值", value=float(df[filter_column].min()))
                max_val = col_max.number_input("最大值", value=float(df[filter_column].max()))

            if st.button("应用数值筛选"):
                df = df[(df[filter_column] >= min_val) & (df[filter_column] <= max_val)]
                st.success(f"✅ 筛选后剩余 {len(df):,} 条数据")

        # ========== 差分计算 ==========
        st.header("📊 差分计算")

        with st.expander("计算差分"):
            diff_column = st.selectbox("选择要计算差分的列", numeric_columns)

            if st.button("计算差分"):
                df = processor.calculate_diff(diff_column)
                st.success(f"✅ 已添加列: {diff_column}_diff")

        # ========== 数据可视化 ==========
        st.header("📉 数据可视化")

        # 图表类型选择
        chart_type = st.selectbox(
            "选择图表类型",
            ["折线图", "柱状图", "散点图", "直方图"]
        )

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if chart_type in ["折线图", "柱状图"]:
            x_col = st.selectbox("X轴", df.columns.tolist())
            y_col = st.selectbox("Y轴", numeric_cols)

            if chart_type == "折线图":
                fig = px.line(df, x=x_col, y=y_col, color='source_folder' if 'source_folder' in df.columns else None)
            else:
                fig = px.bar(df, x=x_col, y=y_col, color='source_folder' if 'source_folder' in df.columns else None)

            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "散点图":
            x_col = st.selectbox("X轴", numeric_cols)
            y_col = st.selectbox("Y轴", [c for c in numeric_cols if c != x_col])
            color_col = st.selectbox("颜色分组", ["无"] + df.columns.tolist())

            fig = px.scatter(df, x=x_col, y=y_col, color=color_col if color_col != "无" else None)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "直方图":
            x_col = st.selectbox("选择列", numeric_cols)
            fig = px.histogram(df, x=x_col, nbins=50)
            st.plotly_chart(fig, use_container_width=True)

        # ========== 数据导出 ==========
        st.header("💾 数据导出")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("导出为 CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="下载 CSV",
                    data=csv,
                    file_name=f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("导出筛选后数据"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="下载筛选后数据",
                    data=csv,
                    file_name=f"filtered_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        # 页脚
        st.markdown("---")
        st.markdown("<center><small>💡 提示: 调整筛选条件后数据会自动更新</small></center>", unsafe_allow_html=True)

    # ========== 模式2: 自定义 HTML 页面 ==========
    else:
        st.markdown('<h1 class="main-title">📊 数据分析平台 (HTML模式)</h1>', unsafe_allow_html=True)
        st.markdown("---")

        # HTML 文件路径
        html_file_path = st.sidebar.text_input(
            "HTML 文件路径",
            value="./csv_visualization_with_data.html",
            help="你的自定义 HTML 文件路径"
        )

        # 检查文件是否存在
        if os.path.exists(html_file_path):
            st.sidebar.success(f"✅ 找到文件: {html_file_path}")

            # 读取并显示 HTML
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 使用 Streamlit 的 html 组件显示
            components.html(html_content, height=800, scrolling=True)

            st.info("💡 这是你自定义的 HTML 页面,嵌入在 Streamlit 中显示")
        else:
            st.error(f"❌ 未找到文件: {html_file_path}")
            st.info("📝 请确保:")
            st.info("1. HTML 文件在项目根目录下")
            st.info("2. 文件名正确(区分大小写)")
            st.info("3. 路径填写正确")


if __name__ == "__main__":
    main()