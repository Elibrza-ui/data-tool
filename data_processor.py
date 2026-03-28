================================================================================
              data_processor.py 完整代码及详细说明
================================================================================

文件名: data_processor.py
作用: 数据处理核心类,提供数据读取、合并、筛选、差分计算等功能


================================================================================
                              完整代码
================================================================================

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


# 示例使用
if __name__ == "__main__":
    # 示例数据路径
    data_path = "./data"

    # 创建数据处理器
    processor = DataProcessor(data_path)

    # 加载数据
    df = processor.load_all_data()

    if not df.empty:
        # 显示统计信息
        summary = processor.get_summary_stats()
        print("\n📈 数据摘要:")
        print(f"总行数: {summary['total_rows']}")
        print(f"总列数: {summary['total_columns']}")
        print(f"文件夹数: {summary['folder_count']}")
        print(f"内存占用: {summary['memory_usage_mb']:.2f} MB")


================================================================================
                         代码详细说明
================================================================================

================================================================================
1. 导入部分
================================================================================

import pandas as pd
    导入pandas库,用于数据处理和分析,是Python数据分析的核心库

import os
    导入os库,用于文件和目录操作,如读取文件夹列表

from typing import List, Dict, Optional
    导入类型提示,用于声明函数参数和返回值的类型,提高代码可读性

from datetime import datetime
    导入datetime,虽然当前代码中未使用,但预留了时间处理能力


================================================================================
2. DataProcessor 类定义
================================================================================

class DataProcessor:
    """数据处理类：读取、合并、差分、筛选"""

定义了一个名为DataProcessor的类,用于处理数据相关操作


================================================================================
3. __init__ 方法 - 初始化
================================================================================

def __init__(self, data_path: str):
    """
    初始化数据处理器

    Args:
        data_path: 数据文件夹路径（包含12个子文件夹）
    """
    self.data_path = data_path
    self.raw_data: List[pd.DataFrame] = []
    self.merged_data: Optional[pd.DataFrame] = None

说明:
  - data_path: 存储数据文件夹的路径
  - raw_data: 存储原始数据的列表,每个元素是一个DataFrame
  - merged_data: 存储合并后的数据


================================================================================
4. load_all_data 方法 - 加载所有数据 ⭐核心方法
================================================================================

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

详细说明:

步骤1: 获取所有文件夹
  folders = sorted([f for f in os.listdir(self.data_path)
                   if os.path.isdir(os.path.join(self.data_path, f))])

  - os.listdir(self.data_path): 列出data_path下的所有文件和文件夹
  - os.path.isdir(): 检查是否是文件夹
  - sorted(): 对文件夹名排序,确保按顺序加载

步骤2: 遍历每个文件夹
  for folder in folders:
      folder_path = os.path.join(self.data_path, folder)

  - 构建完整的文件夹路径

步骤3: 查找CSV文件
  csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

  - 查找文件夹中所有.csv结尾的文件

步骤4: 读取CSV并处理
  if csv_files:
      csv_path = os.path.join(folder_path, csv_files[0])
      try:
          df = pd.read_csv(csv_path)
          df['source_folder'] = folder
          self.raw_data.append(df)

  - pd.read_csv(): 使用pandas读取CSV文件
  - df['source_folder'] = folder: 添加来源文件夹列,标记数据来自哪个文件夹
  - self.raw_data.append(df): 将DataFrame添加到列表中

步骤5: 合并所有数据
  self.merged_data = pd.concat(self.raw_data, ignore_index=True)

  - pd.concat(): 拼接多个DataFrame
  - ignore_index=True: 忽略原索引,重新生成连续索引

返回值:
  - 成功: 返回合并后的DataFrame
  - 失败: 返回空DataFrame


================================================================================
5. filter_by_columns 方法 - 按列筛选
================================================================================

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

说明:
  - 检查列是否在DataFrame中存在
  - 只保留存在的列
  - 返回筛选后的DataFrame

使用示例:
  processor = DataProcessor("./data")
  df = processor.load_all_data()
  df_filtered = processor.filter_by_columns(['temperature', 'humidity'])


================================================================================
6. filter_by_folder 方法 - 按文件夹筛选
================================================================================

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

说明:
  - 检查source_folder列是否存在
  - 使用isin()方法筛选指定文件夹的数据

使用示例:
  df_filtered = processor.filter_by_folder(['day_01', 'day_02'])


================================================================================
7. filter_by_value 方法 - 按数值范围筛选
================================================================================

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

说明:
  - 复制DataFrame,避免修改原始数据
  - 支持单独设置最小值或最大值
  - 也可以同时设置最小值和最大值

使用示例:
  # 只筛选温度大于20的数据
  df_filtered = processor.filter_by_value('temperature', min_val=20)

  # 筛选温度在20-30之间的数据
  df_filtered = processor.filter_by_value('temperature', min_val=20, max_val=30)


================================================================================
8. calculate_diff 方法 - 计算差分 ⭐核心方法
================================================================================

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

详细说明:

差分计算:
  - diff()方法计算相邻行的差值
  - 例如: [1, 2, 3] → [NaN, 1, 1]
  - 第一行没有前一行,所以是NaN(空值)

分组计算:
  - groupby(group_by): 按指定列分组
  - 默认按source_folder分组
  - 这样每个文件夹独立计算差分,不会跨文件夹计算

新增列:
  - 新增列名为 {原列名}_diff
  - 例如: temperature → temperature_diff

使用示例:
  processor = DataProcessor("./data")
  df = processor.load_all_data()

  # 计算温度的差分
  df_with_diff = processor.calculate_diff('temperature')

  # 结果会新增 temperature_diff 列


================================================================================
9. get_summary_stats 方法 - 获取统计信息 ⭐核心方法
================================================================================

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

返回的统计信息:

  total_rows: 总行数
    - DataFrame的总行数
    - 例如: 518400

  total_columns: 总列数
    - DataFrame的总列数
    - 例如: 20

  columns: 列名列表
    - 所有列名的列表
    - 例如: ['timestamp', 'temperature', 'humidity', ...]

  folder_count: 文件夹数量
    - source_folder列的唯一值数量
    - 即加载了多少个文件夹的数据
    - 例如: 12

  dtypes: 数据类型字典
    - 每列的数据类型
    - 例如: {'timestamp': 'object', 'temperature': 'float64', ...}

  memory_usage_mb: 内存占用(MB)
    - DataFrame占用的内存大小
    - 例如: 45.2 MB

使用示例:
  processor = DataProcessor("./data")
  df = processor.load_all_data()

  summary = processor.get_summary_stats()
  print(f"总行数: {summary['total_rows']}")
  print(f"总列数: {summary['total_columns']}")
  print(f"内存占用: {summary['memory_usage_mb']:.2f} MB")


================================================================================
10. get_numeric_columns 方法 - 获取数值型列名
================================================================================

def get_numeric_columns(self) -> List[str]:
    """获取数值型列名"""
    if self.merged_data is None:
        return []

    return self.merged_data.select_dtypes(include=['int64', 'float64']).columns.tolist()

说明:
  - select_dtypes(): 选择特定数据类型的列
  - include=['int64', 'float64']: 只选择整数和浮点数类型
  - columns.tolist(): 将列名转换为列表

使用场景:
  - 在可视化时,只能对数值型数据绘图
  - 在数值筛选时,只能对数值型列设置范围

使用示例:
  numeric_cols = processor.get_numeric_columns()
  # 返回: ['temperature', 'humidity', 'pressure', ...]


================================================================================
11. export_data 方法 - 导出数据
================================================================================

def export_data(self, df: pd.DataFrame, filename: str):
    """
    导出数据为CSV

    Args:
        df: 要导出的DataFrame
        filename: 文件名
    """
    df.to_csv(filename, index=False)
    print(f"✅ 数据已导出: {filename}")

说明:
  - df.to_csv(): 将DataFrame保存为CSV文件
  - index=False: 不保存行索引
  - 保存后打印成功消息

使用示例:
  processor.export_data(df, 'output.csv')


================================================================================
12. 示例使用 - if __name__ == "__main__"
================================================================================

if __name__ == "__main__":
    # 示例数据路径
    data_path = "./data"

    # 创建数据处理器
    processor = DataProcessor(data_path)

    # 加载数据
    df = processor.load_all_data()

    if not df.empty:
        # 显示统计信息
        summary = processor.get_summary_stats()
        print("\n📈 数据摘要:")
        print(f"总行数: {summary['total_rows']}")
        print(f"总列数: {summary['total_columns']}")
        print(f"文件夹数: {summary['folder_count']}")
        print(f"内存占用: {summary['memory_usage_mb']:.2f} MB")

说明:
  - 当直接运行此文件时,执行示例代码
  - 当被其他文件导入时,不执行此部分
  - 用于测试和演示功能


================================================================================
                        在 app.py 中的使用
================================================================================

# 导入类
from data_processor import DataProcessor

# 创建处理器实例
processor = DataProcessor(data_path)

# 加载数据
df = processor.load_all_data()

# 获取统计信息
summary = processor.get_summary_stats()
st.metric("总行数", summary['total_rows'])
st.metric("总列数", summary['total_columns'])

# 按文件夹筛选
df = df[df['source_folder'].isin(selected_folders)]

# 按数值筛选
df = df[(df[filter_column] >= min_val) & (df[filter_column] <= max_val)]

# 计算差分
df = processor.calculate_diff(diff_column)

# 获取数值型列名
numeric_columns = processor.get_numeric_columns()


================================================================================
                            完整使用示例
================================================================================

from data_processor import DataProcessor

# 1. 初始化
processor = DataProcessor("./data")

# 2. 加载数据
df = processor.load_all_data()

# 3. 查看统计信息
summary = processor.get_summary_stats()
print(f"总行数: {summary['total_rows']}")
print(f"总列数: {summary['total_columns']}")
print(f"列名: {summary['columns']}")

# 4. 按文件夹筛选
df = processor.filter_by_folder(['day_01', 'day_02'])

# 5. 按数值筛选
df = processor.filter_by_value('temperature', min_val=20, max_val=30)

# 6. 计算差分
df = processor.calculate_diff('temperature')

# 7. 获取数值型列
numeric_cols = processor.get_numeric_columns()
print(f"数值型列: {numeric_cols}")

# 8. 导出数据
processor.export_data(df, 'result.csv')


================================================================================
                              关键特性总结
================================================================================

1. 自动合并
   - 自动读取多个文件夹的CSV
   - 智能合并数据
   - 添加来源标记

2. 灵活筛选
   - 按列筛选
   - 按文件夹筛选
   - 按数值范围筛选

3. 差分计算
   - 支持分组计算
   - 自动添加差分列
   - 适合时序数据分析

4. 统计信息
   - 快速获取数据概览
   - 包含内存占用
   - 包含数据类型

5. 易于扩展
   - 清晰的类结构
   - 完整的类型提示
   - 详细的文档字符串


================================================================================
                            文档结束
================================================================================

如有问题,请参考:
  - app.py: 查看如何使用这个类
  - README.md: 项目说明
  - 新手教程.md: 详细使用教程

祝使用愉快! 🚀
