"""
文件处理模块
提供CSV文件的合并、筛选等功能
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import List

from datetime import datetime


def read_csv_with_auto_separator(file_path_or_uploaded):
    """尝试自动检测分隔符并读取CSV文件"""
    import io

    # 如果是上传的文件对象，先读取内容
    if hasattr(file_path_or_uploaded, 'read'):
        content = file_path_or_uploaded.read()
        # 如果是上传的文件，需要重置指针
        if hasattr(file_path_or_uploaded, 'seek'):
            file_path_or_uploaded.seek(0)
        # 解码内容
        try:
            text = content.decode('utf-8')
        except:
            try:
                text = content.decode('gbk')
            except:
                text = content.decode('latin-1')
        file_obj = io.StringIO(text)
    else:
        # 本地文件路径
        file_path_or_uploaded = Path(file_path_or_uploaded)
        try:
            text = file_path_or_uploaded.read_text(encoding='utf-8')
        except:
            try:
                text = file_path_or_uploaded.read_text(encoding='gbk')
            except:
                text = file_path_or_uploaded.read_text(encoding='latin-1')
        file_obj = io.StringIO(text)

    # 检测分隔符
    first_line = text.split('\n')[0] if text else ''
    if '\t' in first_line:
        sep = '\t'
    elif ';' in first_line:
        sep = ';'
    else:
        sep = ','

    # 尝试读取文件
    try:
        if hasattr(file_path_or_uploaded, 'read'):
            # 重置文件指针
            if hasattr(file_path_or_uploaded, 'seek'):
                file_path_or_uploaded.seek(0)
            df = pd.read_csv(file_path_or_uploaded, sep=sep, encoding='utf-8')
        else:
            try:
                df = pd.read_csv(file_path_or_uploaded, sep=sep, encoding='utf-8')
            except:
                df = pd.read_csv(file_path_or_uploaded, sep=sep, encoding='gbk')
        return df, sep
    except Exception as e:
        # 最后尝试用默认方式读取
        if hasattr(file_path_or_uploaded, 'read'):
            if hasattr(file_path_or_uploaded, 'seek'):
                file_path_or_uploaded.seek(0)
            df = pd.read_csv(file_path_or_uploaded)
        else:
            df = pd.read_csv(file_path_or_uploaded)
        return df, ','


def render_file_processor_page():
    """渲染文件处理页面"""

    # 添加自定义样式
    st.markdown("""
    <style>
        /* 整体背景色 */
        .stApp {
            background-color: #f0f2f6 !important;
        }
        .stMarkdownContainer{
            color: #ffffff !important;
        }
        /* 主容器背景 */
        .block-container {
            background-color: #f0f2f6 !important;
            max-height: none !important;
            height: auto !important;
            padding-bottom: 100px !important;
        }

        /* 选项卡样式 */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 8px;
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #f1f5f9;
            color: #475569;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.2s;
        }

        .stTabs [aria-selected="true"] {
            background-color: #3b82f6;
            color: #ffffff;
        }

        /* 按钮样式 */
        .stButton > button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.2s;
        }

        .stButton > button:hover {
            background-color: #2563eb;
        }

        /* 输入框样式 */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stMultiselect > div > div > div {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            color: #1e293b;
        }
        
        /* 数据表格样式 */
        .stDataFrame {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* 指标卡片样式 */
        .stMetric {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* 扩展器样式 */
        .streamlit-expanderHeader {
            background-color: ##1890FF;
            border-radius: 6px;
            color: #1e293b;
        }

        /* 滑块样式 */
        .stSlider > div > div > div {
            background-color: #3b82f6;
        }
        .block-container {
        background-color: #f0f2f6 !important;
        padding-bottom: 100px !important;  /* 底部留出100px空间 */
        }
        /* 2. 改上传按钮颜色 */
        .stFileUploader button {
            background-color: #1890FF !important;
            color: white !important;
            border-radius: 6px !important;
        }
        /* 选中 help 对应的问号图标并隐藏 */
        .stTooltipIcon {
            display: none !important;
        }
        .stFileUploaderFileName{
            color: black;
        }
        .stExpander{
            color: black !important;
        }
          .st-emotion-cache-11ofl8m {
            background-color: #f0f2f6 !important;
        }
        .my-black-title {
            color: #000000 !important;
            font-size: 24px !important;
            font-weight: 700 !important;
            margin: 0 0 10px 0 !important;
        }
        .my-black-subtitle {
            color: #000000 !important;
            font-size: 20px !important;
            font-weight: 600 !important;
            margin: 0 0 10px 0 !important;
        }
    </style>
  
    """, unsafe_allow_html=True)
    st.markdown('<p class="my-black-title">📁 文件处理</p>', unsafe_allow_html=True)
    #st.header("📁 文件处理")
    # 创建选项卡
    tab1, tab2 = st.tabs(["合并", "筛选"])

    with tab1:
        merge_files_section()

    with tab2:
        filter_data_section()

def merge_files_section():
    """文件合并区域"""

    # 上传区域
    st.markdown('<p class="my-black-subtitle">📤 上传CSV文件</p>', unsafe_allow_html=True)
    #st.markdown("### 📤 上传CSV文件")
    uploaded_files = st.file_uploader(
        "",
        type=['csv'],
        accept_multiple_files=True,
        help="支持多文件上传",
        key="merge_upload"
    )

    # 同时显示已上传的文件和本地已保存的文件
    all_available_files = []
    upload_dir = Path("uploaded_files")

    # 添加刚刚上传的文件（未保存）
    if uploaded_files:
        st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")

        # 显示文件信息（添加错误处理）
        with st.expander("查看文件详情"):
            for file in uploaded_files:
                try:
                    df, sep = read_csv_with_auto_separator(file)
                    if df.empty:
                        st.warning(f"⚠️ **{file.name}** - 文件为空")
                    else:
                        sep_display = 'Tab' if sep == '\t' else sep
                        st.write(f"**{file.name}** - {len(df)} 行, {len(df.columns)} 列 (分隔符: {sep_display})")
                        st.dataframe(df.head(3))
                        all_available_files.append(file)
                except Exception as e:
                    st.error(f"❌ **{file.name}** - 读取失败: {str(e)}")

    # 添加本地已保存的文件
    if upload_dir.exists():
        csv_files = list(upload_dir.glob("*.csv"))
        all_available_files.extend(csv_files)

    st.markdown("---")

    #st.subheader("🔗 合并多个CSV文件")
    st.markdown('<p class="my-black-subtitle">🔗 合并多个CSV文件</p>', unsafe_allow_html=True)

    if all_available_files:
        selected_files = st.multiselect(
            "选择要合并的文件",
            options=[f.name for f in all_available_files],
            default=[f.name for f in all_available_files[:3]] if len(all_available_files) >= 3 else None
        )

        if selected_files:
            if st.button("🔀 开始合并"):
                with st.spinner("正在合并文件..."):
                    # 根据文件类型选择加载方式（添加错误处理）
                    merged_dfs = []
                    errors = []
                    for file_name in selected_files:
                        try:
                            # 检查是上传的文件还是本地文件
                            uploaded_file = next((f for f in (uploaded_files or []) if f.name == file_name), None)
                            if uploaded_file:
                                df, sep = read_csv_with_auto_separator(uploaded_file)
                                if not df.empty:
                                    df['_source_file'] = uploaded_file.name
                                    merged_dfs.append(df)
                                else:
                                    errors.append(f"{file_name} - 文件为空")
                            else:
                                file_path = upload_dir / file_name
                                df, sep = read_csv_with_auto_separator(file_path)
                                if not df.empty:
                                    df['_source_file'] = file_name
                                    merged_dfs.append(df)
                                else:
                                    errors.append(f"{file_name} - 文件为空")
                        except Exception as e:
                            errors.append(f"{file_name} - {str(e)}")

                    # 显示错误信息
                    if errors:
                        for err in errors:
                            st.warning(f"⚠️ {err}")

                    if merged_dfs:
                        merged_df = pd.concat(merged_dfs, ignore_index=True)
                        st.success(f"✅ 合并成功！共 {len(merged_df)} 行数据")

                        # 显示合并结果
                        st.dataframe(merged_df.head(10))

                        # 显示统计信息
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("总行数", len(merged_df))
                        with col2:
                            st.metric("总列数", len(merged_df.columns))
                        with col3:
                            st.metric("文件数", len(selected_files))

                        # 导出合并结果
                        st.markdown("---")
                        st.subheader("📤 导出合并结果")

                        # 生成临时文件用于下载
                        merged_csv = merged_df.to_csv(index=False)
                        st.download_button(
                            label="⬇️ 导出CSV",
                            data=merged_csv,
                            file_name=f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

                        # 同时保存到本地
                        if st.button("💾 保存到本地"):
                            if not upload_dir.exists():
                                upload_dir.mkdir(exist_ok=True)
                            output_file = upload_dir / f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            merged_df.to_csv(output_file, index=False)
                            st.success(f"✅ 已保存到 {output_file.name}")
    else:
        st.info("📁 请先上传CSV文件")

def filter_data_section():
    """数据筛选区域"""

    # 上传区域
    st.markdown("### 📤 上传CSV文件")
    uploaded_files = st.file_uploader(
        "",
        type=['csv'],
        accept_multiple_files=True,
        help="支持多文件上传",
        key="filter_upload"
    )

    # 获取所有可用文件（包括上传的文件和本地文件）
    all_available_files = []
    upload_dir = Path("uploaded_files")

    # 添加刚刚上传的文件
    if uploaded_files:
        st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")

        # 显示文件信息（添加错误处理）
        with st.expander("查看文件详情"):
            for file in uploaded_files:
                try:
                    df, sep = read_csv_with_auto_separator(file)
                    if df.empty:
                        st.warning(f"⚠️ **{file.name}** - 文件为空")
                    else:
                        sep_display = 'Tab' if sep == '\t' else sep
                        st.write(f"**{file.name}** - {len(df)} 行, {len(df.columns)} 列 (分隔符: {sep_display})")
                        st.dataframe(df.head(3))
                        all_available_files.append(file)
                except Exception as e:
                    st.error(f"❌ **{file.name}** - 读取失败: {str(e)}")

        # 保存文件到本地
        if st.button("💾 保存文件", key="save_filter"):
            save_dir = Path("uploaded_files")
            save_dir.mkdir(exist_ok=True)

            for file in uploaded_files:
                file_path = save_dir / file.name
                with open(file_path, 'wb') as f:
                    f.write(file.getbuffer())

            st.success(f"✅ 文件已保存到 {save_dir.absolute()}")

    # 添加本地已保存的文件
    if upload_dir.exists():
        csv_files = list(upload_dir.glob("*.csv"))
        all_available_files.extend(csv_files)

    st.markdown("---")
    st.subheader("🔍 数据筛选")

    if all_available_files:
        selected_file = st.selectbox(
            "选择要筛选的文件",
            options=[f.name for f in all_available_files],
            index=0
        )

        if selected_file:
            # 根据文件类型选择加载方式（添加错误处理）
            try:
                uploaded_file = next((f for f in (uploaded_files or []) if f.name == selected_file), None)
                if uploaded_file:
                    df, sep = read_csv_with_auto_separator(uploaded_file)
                else:
                    df, sep = read_csv_with_auto_separator(upload_dir / selected_file)

                if df.empty:
                    st.warning("⚠️ 当前文件为空，请选择其他文件")
                    return

                sep_display = 'Tab' if sep == '\t' else sep
                st.info(f"📊 加载了 {len(df)} 行, {len(df.columns)} 列 (分隔符: {sep_display})")
            except Exception as e:
                st.error(f"❌ 读取文件失败: {str(e)}")
                return

            # 选择筛选列
            filter_column = st.selectbox(
                "选择筛选列",
                options=df.columns.tolist(),
                key="filter_column_select"
            )

            if filter_column:
                # 显示该列的数据类型和统计信息
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**数据类型**: {df[filter_column].dtype}")
                with col2:
                    if df[filter_column].dtype in ['int64', 'float64']:
                        st.write(f"**最小值**: {df[filter_column].min()}")
                        st.write(f"**最大值**: {df[filter_column].max()}")

                # 根据数据类型显示不同的筛选选项
                if df[filter_column].dtype in ['int64', 'float64']:
                    st.subheader("数值范围筛选")
                    min_val, max_val = st.slider(
                        f"{filter_column} 范围",
                        float(df[filter_column].min()),
                        float(df[filter_column].max()),
                        (float(df[filter_column].min()), float(df[filter_column].max()))
                    )
                    filtered_df = df[(df[filter_column] >= min_val) & (df[filter_column] <= max_val)]
                else:
                    st.subheader("文本筛选")
                    search_value = st.text_input(f"搜索 {filter_column}")
                    if search_value:
                        filtered_df = df[df[filter_column].astype(str).str.contains(search_value, case=False, na=False)]
                    else:
                        filtered_df = df.copy()

                # 显示筛选结果
                st.write(f"筛选后: {len(filtered_df)} 行")
                st.dataframe(filtered_df.head(20))

                # 导出筛选结果
                st.markdown("---")
                st.subheader("📤 导出筛选结果")

                # 下载按钮
                filtered_csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ 导出CSV",
                    data=filtered_csv,
                    file_name=f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

                # 保存到本地
                if st.button("💾 保存到本地"):
                    if not upload_dir.exists():
                        upload_dir.mkdir(exist_ok=True)
                    output_file = upload_dir / f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    filtered_df.to_csv(output_file, index=False)
                    st.success(f"✅ 已保存到 {output_file.name}")
    else:
        st.info("📁 请先上传CSV文件")



