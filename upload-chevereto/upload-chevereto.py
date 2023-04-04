# -*- coding: utf-8 -*-

import json
import logging
import time
from configparser import ConfigParser

import requests
import argparse
import sys


# 读取配置文件
def read_config(config_path):
    cfg = ConfigParser()
    cfg.read(config_path, encoding='utf-8')
    section_list = cfg.sections()
    config_dict = {}
    for section in section_list:
        section_item = cfg.items(section)
        for item in section_item:
            config_dict[item[0]] = item[1]
    return config_dict


# 按行读取文件的内容，保存成列表
def read_file_to_list(file_path):
    result = []
    with open(file_path, 'r') as f:
        for line in f:
            result.append(line.strip('\n'))
    return result


# 获得本地图片路径后，上传至图床并记录返回的json字段
def up_to_chevereto(img_list):
    for img in img_list:
        # 先判断传过来的是本地路径还是远程图片地址
        if "http" == img[:4]:
            # 非本地图片的话可以考虑下载到本地再上传
            logging.info(img)
            continue
        else:
            try:
                res_json = upload(img)
                parse_response_url(res_json,img)
            except Exception as e:
                logging.error(e)
                logging.error(img+"\tUpload failed")


# 调用 Chevereto API 上传图床
def upload(img):
    files = {'source': open(img, "rb")}
    # 拼接url并上传图片至Chevereto图床
    url = config_dict['chevereto_url'] + "?key=" + config_dict['api_key'] + "&format=json"
    r = requests.post(url, files=files)
    return json.loads(r.text)


# 判断是否上传成功并记录日志
def parse_response_url(json, img_path):
    # 从返回的json中解析字段
    if json['status_code'] != 200:
        logging.info(json['error'])
        logging.info("{}\tupload failure. status_code {} .".format(
            img_path, json['status_code'])
        )
    else:
        img_url = json["image"]["url"]
        # 上传成功的图片url必须用print（logger.info不可以）打印出来，Typora才能识别出是上传成功了，才会自动替换链接。
        print(img_url)
        # 记录上传成功的日志
        upload_log_path = config_dict['upload_log_path']
        with open(upload_log_path, 'a') as file_object:
            upload_log_list = read_file_to_list(config_dict['upload_log_path'])
            year = time.strftime("%Y", time.localtime())
            if "## " + year not in upload_log_list:
                file_object.write("## " + year + "\n\n")
            month = time.strftime("%Y-%m", time.localtime())
            if "## " + month not in upload_log_list:
                file_object.write("## " + month + "\n\n")
            file_object.write(img_url + "  --" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")
            file_object.write("![](" + img_url + ")\n\n")


if __name__ == '__main__':
    # 工具描述及帮助
    TOOL_DESC = """
    A command line tool to upload pictures to chevereto image bed
    """
    logging.info(TOOL_DESC)
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    # 获取参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=str, nargs='+', help="上传图片路径", required=True)
    parser.add_argument('-c', '--config', default="./config.ini", help="读取配置文件", required=True)
    args = parser.parse_args()
    img_list = args.source
    config_path = args.config
    # 读取配置文件
    config_dict = read_config(config_path)
    # 上传图片
    up_to_chevereto(img_list)