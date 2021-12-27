# -*- coding: utf-8 -*-
# @Time : 2020/11/23 11:09 
# @Author : Jiajun LUO
# @File : web_ocr.py
# @Software: PyCharm
# @Function: OCR线上服务


import streamlit as st
import numpy as np
from PIL import Image
import cv2, time
from multiple import *
from table import *
import asyncio

st.set_option('deprecation.showfileUploaderEncoding', False)


def ocr(file_bytes):
    # 调用文字识别服务
    # 获取access token
    token = fetch_token()
    # 拼接通用文字识别高精度url
    image_url = OCR_URL + "?access_token=" + token
    result = request(image_url, urlencode({'image': base64.b64encode(file_bytes)}))

    # 解析返回结果
    result_json = json.loads(result)
    # print(result_json)
    text = ""
    for words_result in result_json["words_result"]:
        # 打印文字
        # print(words_result['words'])
        text = text + words_result["words"] + '\n'
    return text


def main():
    st.title('OCR文字图片识别')
    st.sidebar.title('OCR文字图片识别')

    # 提取普通文字
    st.sidebar.markdown('**提取文字**:memo:')
    # 上传图片并展示
    img_file = st.sidebar.file_uploader("上传一张图片(jpg,png)", type=['png', 'jpg'], key='img')

    if img_file:
        st.sidebar.info('如果要右侧内容消失，请点击以上的×')
        # 将传入的文件转为Opencv格式
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        # 展示图片
        st.image(opencv_image, channels="BGR", use_column_width=True)
        result = ocr(file_bytes)
        st.text_area(label='识别结果', value=result, height=800)

    # 提取表单
    st.sidebar.markdown('**转换表格**:page_facing_up:')
    st.sidebar.success('表单识别功能每天限制使用50次，请谨慎上传图片！')
    table_file = st.sidebar.file_uploader("上传一张表格图片(jpg,png)", type=['png', 'jpg'], key='table')

    if table_file:
        st.sidebar.info('如果要右侧内容消失，请点击以上的×')
        file_bytes = np.asarray(bytearray(table_file.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        # 展示图片
        st.image(opencv_image, channels="BGR", use_column_width=True)
        img_format = base64.b64encode(file_bytes)
        request_id = read_img(img_format)

        with st.spinner("Wait for it..."):
            for i in range(100):
                time.sleep(0.05)
        st.success("Done!")

        st.markdown('获取验证码')
        st.markdown(request_id)

        if request_id:
            request_id = '19585725_2277127'  # 可以输入其他的已经试好的验证码
            download_url = get_img(request_id)
            if download_url:
                st.markdown('点击以下网址,获取表单excel')
                st.write(download_url)
            else:
                st.error('当天使用该功能超过五十次，请明天再试！')
        else:
            st.error('未能成功获取识别结果，如有紧急需求请联系病理大数据部魏博、骆佳俊！')

    ## 按钮控件
    # if st.sidebar.button('Say hello'):
    #     st.write('Why hello there')
    # else:
    #     st.write('Goodbye')

    # # 滚动拉条控件，比如选择连续型参数如学习率
    # age = st.slider('How old are you?', 0, 130, 25)
    # st.write("I'm ", age, 'years old')


if __name__ == '__main__':
    main()
