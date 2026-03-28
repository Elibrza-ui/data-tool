import pandas as pd
import os
from typing import List, Dict, Optional
from datetime import datetime

class DataProcessor:
    """数据处理类：读取、合并、差分、筛选"""

    def __init__(self, data_path: str):
        """
        初始化数据处理器

        Args:
            data_path: 数据文件夹路径（包含12个子文件夹）
        """
        self.data_path = data_path
        self.raw_data: List[pd.DataFrame] = []
        self.merged_data: Optional[pd.DataFrame] = None

    def load_all_data(self) -> pd.DataFrame:
        """
        读取所有文件夹中的CSV文件

        Returns:
            合并后的DataFrame
        """
        self.raw_data = []

        # 遍历所有文件夹
        folders = sorted([f for f in os.listdir(self.data_path)
                         if os.path.isdir(os.path.join(self.data_path, f))])

        for folder in folders:
            folder_path = os.path.join(self.data_path, folder)

            # 查找CSV文件
            csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

            if csv_files:
                csv_path = os.path.join(folder_path, csv_files[0])
                try:
                    df = pd.read_csv(csv_path)
                    # 添加来源文件夹信息
                    df['source_folder'] = folder
                    self.raw_data.append(df)
                    print(f"✅ 已加载: {folder} - {len(df)} 条数据")
                except Exception as e:
                    print(f"❌ 加载失败: {folder} - {e}")

        if self.raw_data:
            self.merged_data = pd.concat(self.raw_data, ignore_index=True)
            print(f"\n📊 总计: 加载 {len(self.raw_data)} 个文件夹, {len(self.merged_data)} 条数据")
            return self.merged_data
        else:
            print("❌ 未找到任何数据文件")
            return pd.DataFrame()

    def filter_by_columns(self, columns: List[str]) -> pd.DataFrame:
        """
        筛选指定列

        Args:
            columns: 要保留的列名列表

        Returns:
            筛选后的DataFrame
        """
        if self.merged_data is None:
            return pd.DataFrame()

        available_columns = [col for col in columns if col in self.merged_data.columns]
        return self.merged_data[available_columns]

    def filter_by_folder(self, folders: List[str]) -> pd.DataFrame:
        """
        按文件夹筛选

        Args:
            folders: 文件夹名称列表

        Returns:
            筛选后的DataFrame
        """
        if self.merged_data is None or 'source_folder' not in self.merged_data.columns:
            return pd.DataFrame()

        return self.merged_data[self.merged_data['source_folder'].isin(folders)]

    def filter_by_value(self, column: str, min_val: float = None, max_val: float = None) -> pd.DataFrame:
        """
        按数值范围筛选

        Args:
            column: 列名
            min_val: 最小值
            max_val: 最大值

        Returns:
            筛选后的DataFrame
        """
        if self.merged_data is None or column not in self.merged_data.columns:
            return pd.DataFrame()

        df = self.merged_data.copy()

        if min_val is not None:
            df = df[df[column] >= min_val]

        if max_val is not None:
            df = df[df[column] <= max_val]

        return df

    def calculate_diff(self, column: str, group_by: str = 'source_folder') -> pd.DataFrame:
        """
        计算差分(相邻行的差值)

        Args:
            column: 要计算差分的列
            group_by: 分组列(默认按文件夹)

        Returns:
            添加了差分列的DataFrame
        """
        if self.merged_data is None or column not in self.merged_data.columns:
            return pd.DataFrame()

        df = self.merged_data.copy()
        df[f'{column}_diff'] = df.groupby(group_by)[column].diff()

        return df

    def get_summary_stats(self) -> Dict:
        """
        获取数据摘要统计

        Returns:
            统计信息字典
        """
        if self.merged_data is None:
            return {}

        summary = {
            'total_rows': len(self.merged_data),
            'total_columns': len(self.merged_data.columns),
            'columns': list(self.merged_data.columns),
            'folder_count': self.merged_data['source_folder'].nunique() if 'source_folder' in self.merged_data.columns else 0,
            'dtypes': self.merged_data.dtypes.to_dict(),
            'memory_usage_mb': self.merged_data.memory_usage(deep=True).sum() / 1024 / 1024
        }

        return summary

    def get_numeric_columns(self) -> List[str]:
        """获取数值型列名"""
        if self.merged_data is None:
            return []

        return self.merged_data.select_dtypes(include=['int64', 'float64']).columns.tolist()

    def export_data(self, df: pd.DataFrame, filename: str):
        """
        导出数据为CSV

        Args:
            df: 要导出的DataFrame
            filename: 文件名
        """
        df.to_csv(filename, index=False)
        print(f"✅ 数据已导出: {filename}")