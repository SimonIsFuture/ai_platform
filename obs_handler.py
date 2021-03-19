import os
import random
import base64
import cv2
import numpy as np
import pandas as pd
import json
import ast
import time
import image_helper
import requests
import logging
from conf import TOKEN, AI_URL, APP_KEY
from flask import Blueprint, render_template, request
obs_manage_opt = Blueprint('obs_manage_opt', __name__)

@obs_manage_opt.route('/', methods=['GET'])
def get_obs():
    # print("object search")
    # 请求的功能参数
    func = request.args.get('f') if request.args.get('f') != None else None
    if func == 'load_data':
        load_pic_num = request.args.get('pic_num') if request.args.get('pic_num') != None else 3  # In default, set 3 pictures
        return load_data(load_pic_num)
    elif func == 'show':
        return render_template("object_search.html")
    else:
        return {}

@obs_manage_opt.route('/', methods=['POST'])
def post():
    values = request.get_data()
    json_data = json.loads(values)
    
    return post_data(json_data)
    # self.write("success")

def get_features(img_name, img_data):
    sess = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=3)
    sess.mount("http://", a)
    headers = {"content-type": "application/json"}
    timeout = 300

    res_data = {
        'Action': 'FaceFeature',
        'ImageData': img_data,
        'time_stamp': time.time() * 1000,
        'ImageName': img_name,
        'AppKey': APP_KEY
    }
    headers = {'content-type': 'application/json'}
    requets_url = AI_URL
    resp_data = json.dumps(res_data)

    resp = sess.post(requets_url, data=resp_data,
                     headers=headers, timeout=timeout)

    if resp.status_code != 200:
        print("Send error.")
        return None
    else:

        res = json.loads(resp.text)
        max_idx = compute_max_face(res['Data']['FaceRectangles'])
        # 根据最大的id来计算需要传出来的数
        features = res['Data']['DenseFeatures'][max_idx*512: (max_idx+1) * 512]
        rectangle = res['Data']['FaceRectangles'][max_idx*4: (max_idx+1) * 4]
        return {
            'features': features,
            'rectangle': rectangle,
            'land_marks': res['Data']['Landmarks']
        }


 # 处理post的请求
def post_data( data):
    # logging.error(data.get)
    # data = json.loads(data)
    # print(data)
    target_url = data['URL']
    action = data['Action']
   
    if action == 'CreateService':
        create_service(app_key=data['AppKey'])
        return
    elif action == 'TopK':
        return topk(data['ImageData'],data['DatSetData'])
        
    sess = requests.Session()
    sess.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
    headers = {"content-type": "application/json"}

    json_data = {}
    for key, value in data.items():
        if key != 'URL':
            json_data[key] = value
    
    resp_data = json.dumps(json_data)
    print(resp_data)
    resp = sess.post(
        target_url,
        data=resp_data,
        headers=headers,
        timeout=100
    )
    if resp.status_code != 200:
        # print(resp.text)
        print("Send fail.")
        return 0
    else:
        json_data = json.loads(resp.text)
        print(json_data)
        # print(json_data)
        if json_data["Code"] == 0:
            print("[SUCESS]")
        else:
            print("[ERROR]")
    return json_data
            
def compute_max_face(face_rectangles):
    np_rec = np.array(face_rectangles).reshape(-1, 4)
    widths = np_rec[:, 2]
    heights = np_rec[:, 3]
    scale = widths * heights
    return np.argmax(scale)

def load_data(intalize_pic_num):
    default_images_dir = os.path.join('static', 'picture', 'default_faces')
    # default_images_dir = '/static/images/default_faces/'
    file_dir_list = os.listdir(default_images_dir)
    images_list = []

    for d in file_dir_list:
        i_path = os.path.join(default_images_dir, d)
        i_images = os.listdir(i_path)
        for ii in i_images:
            images_list.append(os.path.join(i_path, ii))

    file_list = images_list
    del images_list

    # 随机挑选初始图片
    random_file_index = random.sample(
        range(1, len(file_list)), int(intalize_pic_num))
    files = [file_list[i] for i in random_file_index]

    final_data = []  # 最终输出的data
    for file_path in files:
        with open(file_path, 'rb') as f:

            base_64_data = str(base64.urlsafe_b64encode(f.read()), "utf-8")
            # log.info(base_64_data)
            feature_data = get_features(file_path, base_64_data)
            temp_data = {
                'base_64_data': base_64_data,
                'base_64_data_js': None,
                'base_64_data_marked': None,
                'features': feature_data['features'],
                'rectangle': feature_data['rectangle'],
                'land_marks': feature_data['land_marks']
            }
            temp_data['base_64_data_marked'] = get_face_detect_result(temp_data)
            final_data.append(temp_data)
            f.close()
    return topk(final_data[0]['base_64_data'], final_data[1:])


def topk(target_image_data, data_set):
    # 1.
    # log.info(target_image_data.keys())
    # 首先构造数据
    feature_data = get_features(time.time(), target_image_data)
    _target = {
        'base_64_data': target_image_data,
        'base_64_data_marked': None,
        'base_64_data_js': None,
        'features': feature_data['features'],
        'rectangle': feature_data['rectangle'],
        'land_marks': feature_data['land_marks']
    }
    _target['base_64_data_marked'] = get_face_detect_result(_target)
    # 判断target_image_data是否存在于原来的data_set
    all_image_data = [str(d['base_64_data']) for d in data_set]
    if _target['base_64_data'] not in all_image_data:
        data_set.append(_target)
    else:
        df = pd.DataFrame(data_set)
        idx = df[df['base_64_data'] == _target['base_64_data']].index[0]
        data_set[0], data_set[idx] = data_set[idx], data_set[0]

    res_data = data_set
    for key, ds in enumerate(data_set):
        ds['dist'] = compute_cos(_target['features'], ds['features'])
        res_data[key] = ds

    res_data = sorted(res_data, key=lambda x: x['dist'], reverse=True)
    # print(res_data)
    return json.dumps(res_data)


def compute_cos(feature1, feature2):
    A = np.array(feature1).reshape(512, )
    B = np.array(feature2).reshape(512, )
    num = np.dot(A.T, B)
    denom = np.linalg.norm(A) * np.linalg.norm(B)
    dist = abs(num / denom)
    return dist

    # 读取base64编码


def base64_to_image(base64_code):
    # base64解码
    img_data = base64.urlsafe_b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    return img


def image_to_base64(img):
    cv2.imwrite('temp.jpg', img)
    f = open('temp.jpg', 'rb')
    base64_data = str(base64.urlsafe_b64encode(f.read()), "utf-8")
    f.close()
    os.remove('temp.jpg')
    return base64_data

    # 给图片打标


def get_face_detect_result(json_data):
    #
    #   'rectangle': feature_data['rectangle'],
    #   'land_marks': feature_data['Landmarks']
    #
    if json_data is None:
        return False
    landmarks = json_data['land_marks']
    landmarks = np.reshape(landmarks, (-1, 10))
    bboxs = json_data['rectangle']
    bboxs = np.reshape(bboxs, (-1, 4))
    # assert (len(batch_imgs_path) == 1)

    img = base64_to_image(str(json_data['base_64_data']))
    for box, landmark in zip(bboxs, landmarks):
        image_helper.draw_keypoints(img, box, landmark)

    return image_to_base64(img)

