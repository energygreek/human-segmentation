# ffmpeg抠图
要求原视频的背景为纯色高饱和度的背景色的视频抠图效果好，例如纯绿色和纯蓝色。

## ffmpeg命令
下面的命令将原图背景替换为指定的SnowCraterLake.jpg
```sh
ffmpeg  -i ~/Pictures/Wallpapers/SnowCraterLake.jpg -i ~/Downloads/pexels-artem-podrez-7049271.mp4 -filter_complex "[1:v]chromakey=0x2a6a84:similarity=0.1:blend=0.0[ckout];[0:v][ckout]overlay[out]" -map "[out]" -c:v libx264 -f matroska output.mkv
```
说明：
chromakey是ffmpeg的滤镜，用于将指定的颜色替换为透明，overlay将抠图覆盖在新背景图上。要替换颜色以RGB和HEX形式，也支持YUV; similarity是近似度百分百; blend是透明度，0.0表示完全透明。


### 效果
![原视频截图](orign.png)
![换背景后截图](after.png)

## ffmpg包装

changebg 简化了调用ffmpeg的参数，将从sdp文件中读取视频流，并推到指定rtp地址。需要4个参数：
1. sdp文件路径。
2. 新背景文件路径，用户替换原来的背景。
3. 原视频的背景颜色RGB值，16进制。
4. 输出rtp地址。
5. sdp payload。

## 原背景色的问题

由于ffmpeg不支持自动取色，需要手动指定，这与视频电话的需求不符。或者约定一种颜色如绿色，要求打电话的人站在绿布前面。


## 换背景演示
下面三步，先获取720p是视频，然后获取720p的图片，最后替换背景。

### 裁剪得到720p竖屏视频（720x1280）
```
ffmpeg -i ~/Downloads/pexels-artem-podrez-7049271.mp4  -c:v libx264 -preset ultrafast -vf  "scale=720:-1"  ~/Downloads/720.mp4
```
***注意**
1. 使用缩放而不是裁剪，裁剪为720p可能导致显示不完全，缩放则可以保证。
2. 使用缩放命令时，注意导出的画面质量，ffmpeg中，视频默认使用mpeg4的低质量编码，导致画面有锯齿。
```
ffmpeg -i in.mp4 -filter:v "crop=out_w:out_h:x:y" out.mp4
```
改为使用h264则画面质量好很多
```
ffmpeg -i ~/Downloads/pexels-artem-podrez-7049271.mp4 -c:v libx264  -filter:v "crop=720:1280:700:1550" /tmp/output.mp4
```

所以说，当要求目标物体在整个画面的占比大时，选择裁剪。当裁剪导致目标物体被切割时，可以先缩放再裁剪，或先按大的裁剪再缩放。

### 裁剪图片得到背景
```
gm convert ~/Pictures/DesktopPictures/Flower\ 10.jpg    -crop 720x1280+2000+1200 720.jpg 
```

### 替换原视频的背景
```
ffmpeg -re   -i ./small-Wallpapers_SnowCraterLake.jpg  -i ./pexels-artem-podrez-7049271.mp4 -filter_complex "[1:v]chromakey=0x2a6a84:similarity=0.1:blend=0.0[ckout];[0:v][ckout]overlay=x=-400:y=-1600[out]" -map "[out]" -c:v libx264 -preset veryfast  -f rtp rtp://10.8.10.108:10020
```

## 对比抠图

通过对比原背景图，基于差值来抠图。 前提是先有一个背景图（不限制绿色），ffmpeg计算背景图和直播画面，可以将人抠出来。
http://oioiiooixiii.blogspot.com/2016/09/ffmpeg-extract-foreground-moving.html

## 基于深度学习

使用keras_segmentation库来抠图，因为这个库要求tensor的版本，所以在搭建环境时有些麻烦。

### 在百度MDL

1. 先按照tf官网的步骤安装conda虚拟环境。

2. 安装gpu版本的tf
pip install tensorflow-gpu==2.4.1 keras==2.4.1 opencv-python
3. 在终端跑python脚本

### 在阿里天池

conda 使用 python8
!pip install --use-feature=2020-resolver tensorflow==2.4.1 keras==2.4.3 opencv-python

## 基于mediapipe

mediapipe非常完善了，使用简单。