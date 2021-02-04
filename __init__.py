import os
import cv2
from flask import Flask, render_template, send_from_directory, Response
from .get_video_stream import VideoCamera




# def create_app(test_config=None):
#     # create and configure the app
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_mapping(
#         SECRET_KEY='dev',
#         DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
#     )
#
#     if test_config is None:
#         # load the instance config, if it exists, when not testing
#         app.config.from_pyfile('config.py', silent=True)
#     else:
#         # load the test config if passed in
#         app.config.from_mapping(test_config)
#
#     # ensure the instance folder exists
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass
#
#     # a simple page that says hello
#     @app.route('/hello')
#     def hello():
#         with open('flaskr/static/css/video_player.css', 'r') as f:
#             lines = f.readlines()
#             f.close()
#         print(lines)
#         return 'Hello, World!'
#
#     @app.route('/ex')
#     def test_page():
#         return render_template('basic.html')
#
#     @app.route('/video')
#     def video_route():
#         return render_template('video_player.html')
#
#     @app.route('/get_video')
#     def get_video(path):
#         return send_from_directory('js', path)
#     return app
#
#     def gen(camera):
#         while True:
#             frame = camera.get_frame()
#             # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
#             print(frame)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#
#     @app.route('/video_feed')  # 这个地址返回视频流响应
#     def video_feed():
#         return Response(gen(VideoCamera()),
#                         mimetype='multipart/x-mixed-replace; boundary=frame')