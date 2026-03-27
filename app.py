from flask import Flask, render_template

app = Flask(__name__)

# 这里自动加载你的 HTML 前端页面
@app.route('/')
def index():
    return render_template('csv_visualization_with_data.html')

if __name__ == '__main__':
    app.run(debug=True)