# some lib packages...
import json
import logging as log
import base64
import _io

class Utils:
    @staticmethod
    def load_json_data(json_file_path: str):
        data = ''
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            f.close()
        try:
            res = json.loads(data)
            return json.loads(data)
        except Exception as e:
            log.error("Can`t parse file {} into json data, check the file format.".format(json_file_path))
            return json.loads('[]')
    
    @staticmethod
    def post_data(data):
        import json
        import requests
        data = json.loads(data)
        print('---------------------->Begin to request ACTION {}'.format(data['Action']))
        print('---------------------->Request data is {}'.format(data))
        # print(data)
        target_url = data['URL']
        action = data['Action']
        sess = requests.Session()
        sess.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
        headers = {"content-type": "application/json"}
        json_data = {}
        for key, value in data.items():
            if key != 'URL':
                json_data[key] = value

        resp_data = json.dumps(json_data)
        # print(resp_data)
        resp = sess.post(
            target_url,
            data=resp_data,
            headers=headers,
            timeout=100
        )
        if resp.status_code != 200:
            # print(resp.text)
            print("Send fail.")
        else:
            json_data = json.loads(resp.text)
            # print(json_data)
            if json_data["Code"] == 0:
                print("[SUCESS]")
            else:
                print("[ERROR]")
        return(json_data)

    @staticmethod
    def ConvertBase64Data(base_64_data : str):
    # 把Python中的Base64格式转成JS可以用的src
    # data = ((data.image.split(','))[1]).replace(/\//g, "_")
	# data = data.replace(/\+/g, "-")
        return base_64_data.replace("-", "+").replace("_", "/")

    @staticmethod
    def CovertPictureToBase64Data(img_data: str):
        # 把图片转换成为Base64的数据
        #
        return str(base64.urlsafe_b64encode(img_data), "utf-8")


# if __name__ == '__main__':
#     print(Utils.CovertPictureToBase64Data(open('temp/259612838874106710.jpg', 'rb').read()))