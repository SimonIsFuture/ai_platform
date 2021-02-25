from flask import Blueprint, render_template, request
from untils import Utils
import json
import logging as log

video_opt = Blueprint('video_opt', __name__)
util = Utils()

def process_subtitle(file_path):
    # 处理字幕
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        f.close()
    data = []
    for l in lines:
        l_arr = l.split()
        start = float(l_arr[0]) / 1000
        end = float(l_arr[1]) / 1000
        text = l_arr[2]
        data.append({
            'start': start,
            'end': end,
            'text': text
        })
    return data

# Followings are basic handlers
@video_opt.route('/show_detail', methods=['GET'])
def video_route():
    actor_id = int(request.args.get('actor_id')) if request.args.get('actor_id') != None else 0
    current_time = float(request.args.get('current_time')) if request.args.get('current_time') != None else 0
    play_id = int(request.args.get('play_id')) if request.args.get('play_id') != None else 0
    canidate_play_info = util.load_json_data('data/canidate_play.json')
    # to find play id in those data
    play_data = canidate_play_info[play_id]
    
    init_page_json_data = util.load_json_data(play_data['face_data_path'])
    page_data = {
        'play_id': play_id,
        'title': '视频能力',
        'video_src': play_data['video_path'],
        'actor_id': actor_id,
        'face_timeline': init_page_json_data,
        'occur_time': init_page_json_data[actor_id]['occur_time'],
        'current_time': init_page_json_data[actor_id]['occur_time'][0],
    }
    return render_template('video_player.html', ** page_data)

@video_opt.route('/choose_video', methods=['GET'])
def choose_video():
    play_info = util.load_json_data('data/canidate_play.json')
    return render_template('video_choose.html', **{'data': play_info})
 

@video_opt.route('/get_subtitle_data', methods=['GET'])
def get_subtitle():
    play_id = int(request.args.get('play_id')) if request.args.get('play_id') != None else 0
    play_data = util.load_json_data('data/canidate_play.json')[play_id]
    return {'data': (process_subtitle(play_data['subtitle_path']))}

def get_json_data(json_path):
    with open('data/time_dth.json', 'r', encoding='utf-8') as f:
        json_data = f.read()
        f.close()
    return json.loads(json_data)

@video_opt.route('/get_bar', methods=['GET'])
def gen_prcoess_bar():
    actor_id = int(request.args.get('actor_id')) if request.args.get('actor_id') != None else 0
    play_id = int(request.args.get('play_id')) if request.args.get('play_id') != None else 0
    play_data = util.load_json_data('data/canidate_play.json')[play_id]
    #print(play_data)
    total_video_length = int(play_data['play_length'])
    json_data = util.load_json_data(play_data['face_data_path'])
    ouccr_time_list = [ (int(x.split(':')[0]) * 60 + round(float((x.split(':')[1]))) ) for x in json_data[int(actor_id)]['occur_time']]
    return {'process_bar': [x / total_video_length for x in ouccr_time_list]}
