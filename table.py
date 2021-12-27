# -*- coding: utf-8 -*-
# @Time : 2020/11/13 10:46 
# @Author : Jiajun LUO
# @File : table.py 
# @Software: PyCharm
# @Function: 基于表单的识别

import requests
import base64

'''
表格文字识别(异步接口)
使用方式：
1、通过官网获取的AK和SK获取OCR的access_token
2、发送request_url和图片信息作为参数，收到返回的request_id，每天50次
3、使用get_url和request_id，返回表单文件的存储地址result_data，默认保存excel在百度云服务器上

使用参考链接：https://cloud.baidu.com/doc/OCR/s/Ik3h7y238
'''


# # 获取access_token： client_id 为官网获取的AK， client_secret 为官网获取的SK
# host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=29y120bHKovCZOKDy1oSxnyO&client_secret=yYz6EgpAAgi0D584ck7Dd0Mi7CbRu0Zr'
# response = requests.get(host)
# if response:
#     print(response.json())

def get_access_token():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=29y120bHKovCZOKDy1oSxnyO&client_secret=yYz6EgpAAgi0D584ck7Dd0Mi7CbRu0Zr'
    response = requests.get(host)
    if response:
        print(response.json())
        res_dict = response.json()
        return res_dict['access_token']
    else:
        print('无法获取access_token!')



def read_img(img):
    params = {"image": img}
    request_url = "https://aip.baidubce.com/rest/2.0/solution/v1/form_ocr/request"
    access_token = get_access_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        print(response.json())
        res = response.json()
        try:
            reqest_id = res['result'][0]['request_id']
            print(reqest_id, type(reqest_id))
            return reqest_id
        except:
            if 'error_msg' in res:
                if res['error_msg'] == 'Open api daily request limit reached':
                    return 'over limit'
            else:
                return 'unkown msg'


def get_img(request_id):
    ## 根据request_id拿到需要的excel
    get_url = 'https://aip.baidubce.com/rest/2.0/solution/v1/form_ocr/get_request_result'
    access_token = get_access_token()
    get_url = get_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = {"request_id": request_id}
    print("request_id from get_img:", request_id)
    result = requests.post(get_url, data=params, headers=headers)
    if result:
        print(result.json())
        res = result.json()
        ret_msg = res['result']['ret_msg']
        if ret_msg == '图片识别异常' or ret_msg == '进行中':
            return ret_msg
        else:
            download = res['result']['result_data']
            print('download from get_img:', download)
        return download


if __name__ == '__main__':
    # path = "images/表图.png"  # 二进制方式打开图片文件
    # # path = 'images/1.jpg'
    # # 输入文件路径，生成request_id，用于后续的异步get
    # f = open(path, 'rb')
    # img = base64.b64encode(f.read())
    # read_img(img)
    request_id = '19585725_2329868'
    get_img(request_id)


