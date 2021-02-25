from flask import Flask, render_template, send_from_directory, Response
from video_handler import video_opt
from db_handler import db_manage_opt
app = Flask(__name__)
# 注册蓝图，并指定其对应的前缀（url_prefix）
app.register_blueprint(video_opt, url_prefix="/video")
app.register_blueprint(db_manage_opt, url_prefix="/db")


@app.route('/index')
def show_index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=22004, debug=True)
