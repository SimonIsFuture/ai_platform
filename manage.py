from flask import Flask, render_template, send_from_directory, Response
from video_handler import video_opt
from db_handler import db_manage_opt
from obs_handler import obs_manage_opt
from pic_handler import pic_manage_opt
app = Flask(__name__)
# 注册蓝图，并指定其对应的前缀（url_prefix）
# 进行视频播放
app.register_blueprint(video_opt, url_prefix="/video")
# 数据库管理
app.register_blueprint(db_manage_opt, url_prefix="/db")
# 图片管理
app.register_blueprint(pic_manage_opt, url_prefix="/pic")
# 人脸搜索
app.register_blueprint(obs_manage_opt, url_prefix='/obs')

@app.route('/')
def show_index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=22004, debug=True)

