from flask import Blueprint, render_template, request, redirect, url_for
from untils import Utils
import json
import logging as log
import time
import os
from conf import AI_URL, APP_KEY, TOKEN, TEMP_PIC_PATH
pic_manage_opt = Blueprint('pic_manage_opt', __name__)
util = Utils()
post_data = util.post_data
convert_pic_data = util.CovertPictureToBase64Data
covert_base64_to_pic = util.ConvertBase64Data
# 允许上传的文件类型
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG'])

@pic_manage_opt.route('/content_audit', methods=['GET'])
def content_audit():
    args = {'is_first': True}
    return render_template('content_audit.html', **args)

def upload_audit_api( inputs ):
    data = {
            'URL': AI_URL,
            "Action": "ImgCensor",
            "inputs": [inputs],
            "AppKey": APP_KEY,
            'Token': TOKEN,
            "TimeStamp": time.time() * 1000,
        }
    res = post_data(json.dumps(data))
    return res

@pic_manage_opt.route('/upload_pic', methods=['GET', 'POST'])
def upload_pic_upload():
    # desc = request.form.get('desc')  # 获取描述信息
    img = request.files.get('content_pic')  # 获取图片文件
    file_name = str(hash(time.time())) + '.jpg'  # 生成临时文件名
    save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)) + TEMP_PIC_PATH, str(file_name))
    img.save(save_path)  #
    base_64_data = convert_pic_data(save_path)
    res = upload_audit_api(base_64_data)
    os.remove(save_path)
    data = res['Data']
    outputs = data['outputs']
    porn_score = outputs['porn_score']
    politic_score = outputs['politic_score']
    terror_score = outputs['terror_score']
    args = {
        'image_data': covert_base64_to_pic(base_64_data),
        'porn_score': porn_score[0],
        'politic_score': politic_score[0],
        'terror_score': terror_score[0],
        'is_first': False
    }
    return render_template("content_audit.html", **args)