# gstreamer
gstreamer 两个重要工具`gst-launch`和`gst-inspect`
* gst-launch/gst-launch-1.0 - build and run a GStreamer pipeline
* gst-inspect/gst-inspect-1.0 print info about a GStreamer plugin or element


## gst-launch

gst-launch 创建和运行一个'pipeline'， pipeline主要由Element，Element有Properties和preset。如
```
gst-launch-1.0 filesrc location=wdf.mp4  ! qtdemux ! h264parse ! decodebin  ! x264enc ! rtph264pay pt=96 ! udpsink host=127.0.0.1 port=10018 sync=false 
```

`filesrc`是一个element，指示从文件输入, localtion是property

## Elements

qtdemux 用来解mpeg4封装

## opencv 支持gstreamer

从pypi下载的默认都是ffmpeg-backend的版本，如果要支持gstreamer需要自己下载opencv源码编译安装。下载源码后执行cmake配置命令如下。这样会安装到python的安装目录，也就支持python的`import cv2`

```sh
# 克隆opencv仓库后切换到4.x分支
cmake -D CMAKE_BUILD_TYPE=RELEASE 
-D INSTALL_PYTHON_EXAMPLES=ON \
-D INSTALL_C_EXAMPLES=OFF \
-D PYTHON_EXECUTABLE=$(which python3) \
-D BUILD_opencv_python2=OFF \
-D CMAKE_INSTALL_PREFIX=$(python -c "import sys; print(sys.prefix)") \
-D PYTHON3_EXECUTABLE=$(which python) \
-D PYTHON3_INCLUDE_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
-D PYTHON3_PACKAGES_PATH=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
-D WITH_GSTREAMER=ON \
-D BUILD_EXAMPLES=ON ..
```

# 推流
gst-launch-1.0 filesrc location=wdf.mp4  ! qtdemux ! h264parse ! decodebin  ! x264enc ! rtph264pay pt=96 ! udpsink host=127.0.0.1 port=10018 sync=false 

## 简化

gst-launch-1.0 filesrc location=wdf.mp4  ! qtdemux ! rtph264pay pt=96 ! udpsink host=127.0.0.1 port=10018

# 收流
gst-launch-1.0 -v udpsrc address=127.0.0.1 port=10018 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96"  ! rtph264depay ! decodebin ! autovideosink

## 简化
gst-launch-1.0 -v udpsrc address=127.0.0.1 port=10018 ! application/x-rtp !  rtph264depay ! decodebin  ! autovideosink

## 录流

gst-launch-1.0  udpsrc port=10020 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! x264enc ! matroskamux  !  filesink location=record.mkv