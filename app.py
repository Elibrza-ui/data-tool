from flask import Flask, request, send_file, render_template_string
import pandas as pd
import io

app = Flask(__name__)

# 前端页面
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>数据处理工具</title>
</head>
<body>
    <h1>📊 CSV 大数据处理</h1>
    <form action="/process" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv" required>
        <button type="submit">上传并处理</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# 处理 CSV
@app.route('/process', methods=['POST'])
def process_file():
    file = request.files['file']
    if not file:
        return "未选择文件"

    # 读取大数据（pandas 高效处理）
    df = pd.read_csv(file)

    # ====================== 你的数据处理逻辑 ======================
    # 在这里写你的 Python 代码，比如电池数据计算、电压分析、容量统计
    # 示例：新增一列 = 电压 × 电流
    if '电压' in df.columns and '电流' in df.columns:
        df['功率(W)'] = df['电压'] * df['电流']
    # =============================================================

    # 返回处理后的文件
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        download_name="处理结果.csv"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)