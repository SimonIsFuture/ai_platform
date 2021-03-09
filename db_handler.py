from flask import Blueprint, render_template, request, redirect, url_for
from untils import Utils
import json
import logging as log
from conf import TOKEN
import urllib.parse

URl = 'http://182.42.255.14:8502/ai'
db_manage_opt = Blueprint('db_manage_opt', __name__)
util = Utils()
post_data = util.post_data

@db_manage_opt.route('/login', methods=['GET'])
def show_login():
    return render_template('db_login.html')

@db_manage_opt.route('/show', methods=['GET'])
def show_idnex_page():
    appkey = request.args.get('ak') if request.args.get('ak') != None else 0
    db_name = request.args.get('db_name') if request.args.get('db_name') != None else 0
    data = {
        'URL': URl,
        "Action": "ListFaceDbs",
        "AppKey": appkey, 
        "Token": TOKEN
    }
    res = post_data(json.dumps(data))
    db_names = res['Data']['DbList']
    args = {
        'db_names': db_names
    }
    return render_template("db_index.html", **args)

@db_manage_opt.route('/upload_entity', methods=['POST'])
def AddDbEntities():
        appkey = request.form.get('app_key') if request.form.get('app_key') != None else 0
        entity_id = request.form.get('entity_id') if request.form.get('entity_id') != None else 0
        labels = request.form.get('labels') if request.form.get('labels') != None else 0
        data = {
            'URL': URl,
            "Action": "AddFaceEntity",
            "DbName": "default",
            "EntityId": entity_id,
            "Labels": labels,
            "AppKey": appkey
        }
        res = post_data(json.dumps(data))
        return res

@db_manage_opt.route('/ListFaceEntities', methods=['GET'])
def ListFaceEntities():
        page = int(request.args.get('page')) if request.args.get('page') != None else 0
        limit =  int(request.args.get('limit')) if request.args.get('limit') != None else 0
        appkey = request.args.get('app_key') if request.args.get('app_key') != None else 0
        db_name = request.args.get('db_name') if request.args.get('db_name') != None else 0
        data = {
                'URL': URl,
                "Action": "ListFaceEntities",
                "DbName": db_name,
                "Offset": 0,
                "AppKey": appkey,
                'Token': TOKEN
            }
        res = post_data(json.dumps(data))
        print(res)
        
        if res['Code'] == -6:
            log.info('{} has not registered yet.'.format(appkey))
            data = {
                'URL': URl,
                'Action': 'CreateFaceDb',
                'AppKey': appkey,
                'Name': 'default'
            }
            res = post_data(json.dumps(data))
            return ListFaceEntities()
        elif res['Code'] == -7:
            log.info('77777')
        else:
            res=res['Data']
            log.info(res)
            face_entity_res = {
                "code": 0,
                "msg": "",
                "count": res['TotalCount'],
                "data": res['Entities'][page*limit - limit: page*limit]
                }
            return face_entity_res

@db_manage_opt.route('/delete_entity', methods=['GET'])       
def DeleteFaceEentity():
        appkey = request.args.get('app_key') if request.args.get('app_key') != None else 0
        entity_id = request.args.get('entity_id') if request.args.get('entity_id') != None else 0
        data = {
            'Action': 'DeleteFaceEntity',
            'DbName': 'default',
            'EntityId': entity_id,
            'AppKey': appkey,
            'URL': URl
        }
        res = post_data(json.dumps(data))
        return res

def GetEntityInfo(ei, ak, db_name):
    data1 = { # 第一次请求Data的接口 
        'URL': URl,
        "Action": "GetFaceEntity",
        "DbName": "default",
        "EntityId": ei,
        "Detail": 1,
        'AppKey': ak,
        'DbName': db_name
    }
    
    res = post_data(json.dumps(data1))
    # log.info(res)
    res = res['Data']
    faces = res['Faces']
    # 转换一下imgaedata
    final_faces = []
    for f in faces:
        final_faces.append(
            {
                'FacedId': f['FaceId'],
                'ImageData': util.ConvertBase64Data(f['ImageData'])
            }
        )

    labels = res['Labels']
    basic_info = {
        'EntityId': ei,
        'FacesCount': len(faces),
        'Labels': labels,
        'Faces': final_faces,
        'DbName': db_name
    }
    return basic_info

def UploadFaceEntity(entity_id,  app_key, base_64_data, db_name):
    data = {
        'Action': 'AddFace',
        'URL': URl,
        'DbName': 'default',
        'EntityId': entity_id,
        'ImageData': base_64_data,
        'AppKey': app_key,
        "DbName": db_name
    }
    res = post_data(json.dumps(data))
    log.info(res)
    
def DeleteFaceEntity(self):
    face_id = self.get_argument('face_id')
    log.info(face_id)
    data = {
        'Action': 'DeleteFace',
        'URL': URl,
        'DbName': 'default',
        'FaceId': face_id,
        'AppKey': self.app_key
    }
    res = post_data(json.dumps(data))
    self.finish(res)

@db_manage_opt.route('/show_detail', methods=['GET'])    
def show_face_detail():
    app_key = request.args.get('ak') if request.args.get('ak') != None else 0
    ei = request.args.get('ei') if request.args.get('ei') != None else 0
    db_name = request.args.get('db_name') if request.args.get('db_name') != None else 0
    basic_info = GetEntityInfo(ei, app_key, db_name)
    return render_template('db_detail.html', **basic_info)

@db_manage_opt.route('/upload_face', methods=['POST'])  
def upload_face():
    base_64_data = str(request.form.get('file')) if request.form.get('file') != None else 0
    entity_id = request.form.get('ei') if request.form.get('ei') != None else 0
    app_key = str(request.form.get('ak')) if request.form.get('ak') != None else 0
    db_name = request.form.get('db_name') if request.form.get('db_name') != None else 0

    UploadFaceEntity(entity_id, app_key, base_64_data, urllib.parse.unquote(db_name))
    return ("success")

@db_manage_opt.route('/delete_face', methods=['GET'])  
def DeleteFaceEntity():
    face_id = request.args.get('face_id') if request.args.get('face_id') != None else 0
    app_key = request.args.get('ak') if request.args.get('ak') != None else 0
    db_name = request.args.get('db_name') if request.args.get('db_name') != None else 0
    log.info(face_id)
    data = {
        'Action': 'DeleteFace',
        'URL': URl,
        'DbName': 'default',
        'FaceId': face_id,
        'AppKey': app_key,
        'DbName': urllib.parse.unquote(db_name)
    }
    res = post_data(json.dumps(data))
    return (res)

@db_manage_opt.route('/create_new_db', methods=['POST'])  
def AddNewDatabase():
    app_key = request.form.get('app_key') if request.form.get('app_key') != None else 0
    db_name = request.form.get('db_name') if request.form.get('db_name') != None else 0
    data = {
        'Action': 'CreateFaceDb',
        'URL': URl,
        'AppKey': app_key,
        'Name': urllib.parse.unquote(db_name)
    }
    res = post_data(json.dumps(data))
    return res