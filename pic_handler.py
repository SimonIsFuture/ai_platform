from flask import Blueprint, render_template, request, redirect, url_for
from untils import Utils
import json
import logging as log
from conf import AI_URL, TEMP_PIC_PATH, APP_KEY, TOKEN
import time
import os

pic_manage_opt = Blueprint('pic_manage_opt', __name__)
util = Utils()
post_data = util.post_data
# 允许上传的文件类型
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG'])

@pic_manage_opt.route('/content_audit', methods=['GET'])
def content_audit():
    return render_template('content_audit.html')

def upload_audit_api(e):
    data = {
            'URL': AI_URL,
            "Action": "ImgCensor",
            "EntityId": entity_id,
            "inputs": labels,
            "AppKey": APP_KEY,
            'Token': TOKEN
        }
    pass

@pic_manage_opt.route('/upload_pic', methods=['GET', 'POST'])
def upload_pic_upload():
    # desc = request.form.get('desc')  # 获取描述信息
    img = request.files.get('content_pic')  # 获取图片文件
    file_name = str(hash(time.time())) + '.jpg' # 生成临时文件名
    print(os.path.realpath(__file__))
    img.save(os.path.join(os.path.abspath(os.path.dirname(__file__)) + TEMP_PIC_PATH, str(file_name)))  # 保存文件

