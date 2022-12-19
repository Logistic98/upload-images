# -*- coding: utf-8 -*-

import argparse
import sys

import logging
import os
import time

from minio import Minio
from minio.error import S3Error
from configparser import ConfigParser


# 读取配置文件
def read_config(config_path):
    cfg = ConfigParser()
    cfg.read(config_path, encoding='utf-8')
    minio_url = cfg.get('minio', 'minio_url')
    minio_domain = cfg.get('minio', 'minio_domain')
    access_key = cfg.get('minio', 'access_key')
    secret_key = cfg.get('minio', 'secret_key')
    minio_bucket = cfg.get('minio', 'minio_bucket')
    upload_log_path = cfg.get('log', 'upload_log_path')
    config_dict = {}
    config_dict['minio_url'] = minio_url
    config_dict['minio_domain'] = minio_domain
    config_dict['access_key'] = access_key
    config_dict['secret_key'] = secret_key
    config_dict['minio_bucket'] = minio_bucket
    config_dict['upload_log_path'] = upload_log_path
    return config_dict


# 按行读取文件的内容，保存成列表
def read_file_to_list(file_path):
    result = []
    with open(file_path, 'r') as f:
        for line in f:
            result.append(line.strip('\n'))
    return result


# 初始化minio客户端
def get_minio_client(config_dict):
    # 使用endpoint、access key和secret key来初始化minioClient对象。
    minio_client = Minio(config_dict['minio_url'],
                         access_key=config_dict['access_key'],
                         secret_key=config_dict['secret_key'],
                         secure=False)
    return minio_client


# 创建一个存储桶（判断桶是否已经存在，不存在则创建，存在忽略）
def minio_make_bucket_ifnotexist(minio_client, bucket_name):
    bucket_name = bucket_name.replace('_', "-")
    try:
        if not minio_client.bucket_exists(bucket_name):
            logging.info("该存储桶不存在：" + bucket_name)
            minio_client.make_bucket(bucket_name)
            logging.info("存储桶创建：" + bucket_name)
    except S3Error as e:
        if "InvalidAccessKeyId" in str(e):
            logging.error("minio 的 access_key 可能有误")
        elif "SignatureDoesNotMatch" in str(e):
            logging.error("minio 的 secret_key 可能有误")
        else:
            logging.error("minio 的 endpoint、access_key、secret_key 可能有误")
        raise e


# 文件上传
def minio_upload_file(minio_client, bucket_name, object_name, file_path):
    logging.info(file_path)
    result = minio_client.fput_object(bucket_name, object_name, file_path)
    return result


# 获取object_name（上传到minio的路径）
def get_object_name(file_path):
    file_dir, file_full_name = os.path.split(file_path)
    return file_full_name


if __name__ == '__main__':
    # 工具描述及帮助
    TOOL_DESC = """
    A command line tool to upload files to minio
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
    # 初始化minio客户端
    minio_client = get_minio_client(config_dict)
    # 创建一个存储桶（判断桶是否已经存在，不存在则创建，存在忽略）
    minio_make_bucket_ifnotexist(minio_client, config_dict['minio_bucket'])
    # 文件上传minio
    for img_path in img_list:
        object_name = get_object_name(img_path)
        img_url = "https://" + config_dict['minio_domain'] + "/" + config_dict['minio_bucket'] + "/" + object_name
        try:
            minio_upload_file(minio_client, config_dict['minio_bucket'], object_name, img_path)
            with open(config_dict['upload_log_path'], 'a') as file_object:
                upload_log_list = read_file_to_list(config_dict['upload_log_path'])
                year = time.strftime("%Y", time.localtime())
                if "## " + year not in upload_log_list:
                    file_object.write("## " + year + "\n\n")
                month = time.strftime("%Y-%m", time.localtime())
                if "## " + month not in upload_log_list:
                    file_object.write("## " + month + "\n\n")
                file_object.write(img_url + "  --" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")
                file_object.write("![](" + img_url + ")\n\n")
                # 上传成功的图片url必须用print（logger.info不可以）打印出来，Typora才能识别出是上传成功了，才会自动替换链接。
                print(img_url)
        except Exception as e:
            logging.error(e)
            logging.error("上传minio失败")