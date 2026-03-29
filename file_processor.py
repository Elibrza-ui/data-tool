"""
文件处理模块
提供CSV文件的读取、合并、筛选、导出等功能
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import os
from typing import List, Optional
import zipfile
from datetime import datetime


def render_file_processor_page():
    """渲染文件处理页面"""

    # 添加自定义样式
    st.markdown("""
    <style>
        /* 整体背景色 */
        .stApp {
            background-color: #f0f2f6 !important;
        }

        /* 主容器背景 */
        .block-container {
            background-color: #f0f2f6 !important;
        }

        /* 标题样式 */
        h1, h2, h3 {
            color: #1e293b !important;
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
            background-color: #ffffff;
            border-radius: 6px;
            color: #1e293b;
        }

        /* 滑块样式 */
        .stSlider > div > div > div {
            background-color: #3b82f6;
        }
    </style>
    """, unsafe_allow_html=True)

    st.header("📁 文件处理")

    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["合并文件", "数据筛选", "导出数据"])

    with tab1:
        merge_files_section()

    with tab2:
        filter_data_section()

    with tab3:
        export_data_section()


def upload_files_section():
    """文件上传区域"""
    st.subheader("📤 上传CSV文件")
    
    uploaded_files = st.file_uploader(
        "选择要上传的CSV文件",
        type=['csv'],
        accept_multiple_files=True,
        help="支持多文件上传"
    )
    
    if uploaded_files:
        st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")
        
        # 显示文件信息
        with st.expander("查看文件详情"):
            for file in uploaded_files:
                df = pd.read_csv(file)
                st.write(f"**{file.name}** - {len(df)} 行, {len(df.columns)} 列")
                st.dataframe(df.head(3))

@st.cache_data
def load_and_merge_files(file_list: List) -> pd.DataFrame:
    """加载并合并多个CSV文件"""
    dfs = []
    for file in file_list:
        df = pd.read_csv(file)
        df['_source_file'] = file.name
        dfs.append(df)
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


def merge_files_section():
    """文件合并区域"""

    # 上传区域
    st.markdown("### 📤 上传CSV文件")
    uploaded_files = st.file_uploader(
        "",
        type=['csv'],
        accept_multiple_files=True,
        help="支持多文件上传",
        key="merge_upload"
    )

    # 同时显示已上传的文件和本地已保存的文件
    all_available_files = []

    # 添加刚刚上传的文件（未保存）
    if uploaded_files:
        st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")
        all_available_files.extend(uploaded_files)

        # 显示文件信息
        with st.expander("查看文件详情"):
            for file in uploaded_files:
                df = pd.read_csv(file)
                st.write(f"**{file.name}** - {len(df)} 行, {len(df.columns)} 列")
                st.dataframe(df.head(3))

    # 添加本地已保存的文件
    upload_dir = Path("uploaded_files")
    if upload_dir.exists():
        csv_files = list(upload_dir.glob("*.csv"))
        all_available_files.extend(csv_files)

    st.markdown("---")
    st.subheader("🔗 合并多个CSV文件")

    if all_available_files:
        selected_files = st.multiselect(
            "选择要合并的文件",
            options=[f.name for f in all_available_files],
            default=[f.name for f in all_available_files[:3]]
        )

        if selected_files:
            if st.button("🔀 开始合并"):
                with st.spinner("正在合并文件..."):
                    # 根据文件类型选择加载方式
                    merged_dfs = []
                    for file_name in selected_files:
                        # 检查是上传的文件还是本地文件
                        uploaded_file = next((f for f in (uploaded_files or []) if f.name == file_name), None)
                        if uploaded_file:
                            df = pd.read_csv(uploaded_file)
                            df['_source_file'] = uploaded_file.name
                        else:
                            file_path = upload_dir / file_name
                            df = pd.read_csv(file_path)
                            df['_source_file'] = file_name
                        merged_dfs.append(df)

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

                        # 保存合并结果
                        if st.button("💾 保存合并结果"):
                            if not upload_dir.exists():
                                upload_dir.mkdir(exist_ok=True)
                            output_file = upload_dir / f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            merged_df.to_csv(output_file, index=False)
                            st.success(f"✅ 已保存到 {output_file.name}")
    else:
        st.info("📁 请先上传CSV文件")
    
    # 选择要合并的文件
    upload_dir = Path("uploaded_files")
    if upload_dir.exists():
        csv_files = list(upload_dir.glob("*.csv"))
        
        if csv_files:
            selected_files = st.multiselect(
                "选择要合并的文件",
                options=[f.name for f in csv_files],
                default=[f.name for f in csv_files[:3]]
            )
            
            if selected_files:
                selected_file_paths = [upload_dir / f for f in selected_files]
                
                if st.button("🔀 开始合并"):
                    with st.spinner("正在合并文件..."):
                        merged_df = load_and_merge_files(selected_file_paths)
                        
                        if not merged_df.empty:
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
                            
                            # 保存合并结果
                            if st.button("💾 保存合并结果"):
                                output_file = upload_dir / f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                merged_df.to_csv(output_file, index=False)
                                st.success(f"✅ 已保存到 {output_file.name}")
                        else:
                            st.error("❌ 合并失败")
        else:
            st.info("📁 上传目录中没有CSV文件，请先上传文件")
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

    if uploaded_files:
        st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")

        # 显示文件信息
        with st.expander("查看文件详情"):
            for file in uploaded_files:
                df = pd.read_csv(file)
                st.write(f"**{file.name}** - {len(df)} 行, {len(df.columns)} 列")
                st.dataframe(df.head(3))

        # 保存文件到本地
        if st.button("💾 保存文件", key="save_filter"):
            save_dir = Path("uploaded_files")
            save_dir.mkdir(exist_ok=True)

            for file in uploaded_files:
                file_path = save_dir / file.name
                with open(file_path, 'wb') as f:
                    f.write(file.getbuffer())

            st.success(f"✅ 文件已保存到 {save_dir.absolute()}")

    st.markdown("---")
    st.subheader("🔍 数据筛选")
    
    # 加载合并后的文件
    upload_dir = Path("uploaded_files")
    merged_files = list(upload_dir.glob("merged_*.csv")) if upload_dir.exists() else []
    
    if merged_files:
        selected_file = st.selectbox(
            "选择要筛选的文件",
            options=[f.name for f in merged_files],
            index=0
        )
        
        if selected_file:
            df = pd.read_csv(upload_dir / selected_file)
            st.info(f"📊 加载了 {len(df)} 行数据")
            
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
                if st.button("💾 导出筛选结果"):
                    output_file = upload_dir / f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    filtered_df.to_csv(output_file, index=False)
                    st.success(f"✅ 已导出到 {output_file.name}")
    else:
        st.info("📁 没有可筛选的文件，请先合并文件")


def export_data_section():
    """数据导出区域"""

    # 上传区域
    st.markdown("### 📤 上传CSV文件")
    uploaded_files = st.file_uploader(
        "",
        type=['csv'],
        accept_multiple_files=True,
        help="支持多文件上传",
        key="export_upload"
    )

    if uploaded_files:
        st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")

        # 显示文件信息
        with st.expander("查看文件详情"):
            for file in uploaded_files:
                df = pd.read_csv(file)
                st.write(f"**{file.name}** - {len(df)} 行, {len(df.columns)} 列")
                st.dataframe(df.head(3))

        # 保存文件到本地
        if st.button("💾 保存文件", key="save_export"):
            save_dir = Path("uploaded_files")
            save_dir.mkdir(exist_ok=True)

            for file in uploaded_files:
                file_path = save_dir / file.name
                with open(file_path, 'wb') as f:
                    f.write(file.getbuffer())

            st.success(f"✅ 文件已保存到 {save_dir.absolute()}")

    st.markdown("---")
    st.subheader("📤 导出数据")
    
    upload_dir = Path("uploaded_files")
    if not upload_dir.exists():
        upload_dir.mkdir(exist_ok=True)
    
    # 列出所有文件
    all_files = []
    if upload_dir.exists():
        all_files = list(upload_dir.glob("*.csv"))
    
    if all_files:
        # 显示文件列表
        st.write(f"📁 共有 {len(all_files)} 个文件")
        
        # 选择要导出的文件
        export_file = st.selectbox(
            "选择要导出的文件",
            options=[f.name for f in sorted(all_files, key=lambda x: x.stat().st_mtime, reverse=True)],
            index=0
        )
        
        if export_file:
            file_path = upload_dir / export_file
            
            # 显示文件信息
            df = pd.read_csv(file_path)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("行数", len(df))
            with col2:
                st.metric("列数", len(df.columns))
            with col3:
                file_size = file_path.stat().st_size / 1024
                st.metric("文件大小", f"{file_size:.2f} KB")
            
            # 下载按钮
            with open(file_path, 'rb') as f:
                st.download_button(
                    label="⬇️ 下载文件",
                    data=f,
                    file_name=export_file,
                    mime="text/csv"
                )
            
            # 预览数据
            with st.expander("👀 预览数据"):
                st.dataframe(df.head(10))
            
            # 打包下载选项
            if st.button("📦 打包下载所有文件"):
                zip_filename = upload_dir / f"all_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for file in all_files:
                        zipf.write(file, file.name)
                
                with open(zip_filename, 'rb') as f:
                    st.download_button(
                        label="⬇️ 下载压缩包",
                        data=f,
                        file_name=zip_filename.name,
                        mime="application/zip"
                    )
                
                st.success(f"✅ 已打包 {len(all_files)} 个文件")
    else:
        st.info("📁 没有可导出的文件，请先上传文件")
