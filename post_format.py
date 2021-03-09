# 统一管理数据的请求
from conf import AI_URL, APP_KEY, TOKEN

def ListFaceEntities(DbName='default', Offset=1, AppKey, Token):
    ACTION = 'ListFaceEntities'
    post_data = {
        ''
    }