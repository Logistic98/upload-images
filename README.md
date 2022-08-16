## upload-images

项目简介：实现自动上传 Chevereto 私有图床和 Minio 对象存储的脚本，可与 Typora 的 Custom Command 功能搭配使用。详见我的博客：[搭建Minio对象存储及Chevereto私有图床](https://www.eula.club/搭建Minio对象存储及Chevereto私有图床.html)

项目结构：

```
.
├── requirements.txt
├── upload-chevereto
│   ├── config.ini
│   └── upload-chevereto.py
└── upload-minio
    ├── config.ini
    └── upload-minio.py
```

项目依赖：

requirements.txt

```
minio==7.1.11
requests==2.27.1
```



