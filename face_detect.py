from math import atan2
import cv2
import mediapipe as mp
import numpy as np


mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
# glasses 瞳距为600px, 高度500px
# 读入贴图，cv2.imrad('src_path', -1)其中-1表示保留alpha透明通道
sticker = cv2.imread("./glasses.png", -1)
(sticker_h, sticker_w) = sticker.shape[:2]
aspect_ratio = sticker_h/sticker_w
glasses_weight = sticker_w/2
# cv2.imshow("test", sticker)
# cv2.waitKey(0)
old_eye_width = 0


def draw_mark(x, y, sticker, image):
    # 读入底图
    x_offset = int(x - sticker.shape[1]*0.5)  # 贴图位置的左上角坐标：x,y
    y_offset = int(y - sticker.shape[0]*0.5)
    # 计算贴图位置，注意防止超出边界的情况
    x1, x2 = max(x_offset, 0), min(
        x_offset + sticker.shape[1], image.shape[1])
    y1, y2 = max(y_offset, 0), min(
        y_offset + sticker.shape[0], image.shape[0])
    sticker_x1 = max(0, -x_offset)
    sticker_x2 = sticker_x1 + x2 - x1
    sticker_y1 = max(0, -y_offset)
    sticker_y2 = sticker_y1 + y2 - y1
    # 贴图中透明部分的处理
    alpha_h = sticker[sticker_y1:sticker_y2, sticker_x1:sticker_x2, 3] / 255
    alpha = 1 - alpha_h
    # 按4个通道合并图片
    for channel in range(0, 3):
        image[y1:y2, x1:x2, channel] = (
            alpha_h * sticker[sticker_y1:sticker_y2, sticker_x1:sticker_x2,
                              channel] + alpha * image[y1:y2, x1:x2,
                                                              channel])


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def draw_glasses(image, detection):
    l_eye_pos = mp_face_detection.get_key_point(
        detection, mp_face_detection.FaceKeyPoint.LEFT_EYE)
    r_eye_pos = mp_face_detection.get_key_point(
        detection, mp_face_detection.FaceKeyPoint.RIGHT_EYE)
    nose_pos = mp_face_detection.get_key_point(
        detection, mp_face_detection.FaceKeyPoint.NOSE_TIP)
    mouse_center = mp_face_detection.get_key_point(
        detection, mp_face_detection.FaceKeyPoint.MOUTH_CENTER)
    l_ear_pos = mp_face_detection.get_key_point(
        detection, mp_face_detection.FaceKeyPoint.LEFT_EAR_TRAGION)
    r_ear_pos = mp_face_detection.get_key_point(
        detection, mp_face_detection.FaceKeyPoint.RIGHT_EAR_TRAGION)

    new_sticker = sticker
    new_eye_width = l_eye_pos.x - r_eye_pos.x

    global old_eye_width
    # use nose x and eye y
    if abs(old_eye_width - new_eye_width) > 0:
        scale_ratio = image.shape[1] * new_eye_width/glasses_weight
        new_width = int(sticker_w * scale_ratio)
        if new_width > 0:
            new_sticker = cv2.resize(
                sticker, (new_width, int(new_width*aspect_ratio)))

        # rotate make sticker bigger
        radian = atan2((l_eye_pos.y - r_eye_pos.y), (l_eye_pos.x - r_eye_pos.x));
        angle = radian * 180 / 3.1415926;
        new_sticker = rotate_bound(new_sticker, angle)

        old_eye_width = new_eye_width

    # rotate
    draw_mark(image.shape[1] * (l_eye_pos.x + r_eye_pos.x)/2,
              image.shape[0] * (l_eye_pos.y + r_eye_pos.y)/2, new_sticker, image)

def open_caputure():
    pipe_in_example = ' udpsrc address=127.0.0.1 port=10018 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink '
    pipe_in = " udpsrc address=127.0.0.1 port=10018 ! application/x-rtp ! rtph264depay ! decodebin ! videoconvert ! appsink "
    
    #cap = cv2.VideoCapture(source_sdp, cv2.CAP_FFMPEG)
    cap = cv2.VideoCapture(pipe_in_example, cv2.CAP_GSTREAMER)
    print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return cap


def open_writer():
    pipe_out = " appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! rtph264pay ! udpsink host=127.0.0.1 port=10020 "
    writer = cv2.VideoWriter(pipe_out, cv2.CAP_GSTREAMER, 0, 20, (1280, 720), True)
    return writer


if __name__ == '__main__':

    with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5) as face_detection:
        
        cap = open_caputure()
        writer = open_writer()
        if not cap.isOpened():
            print("cap not opened")
            exit(1)
        elif not writer.isOpened():
            print("writer not opened")
            exit(1)

        while True:
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(image)

            # Draw the face detection annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.detections:
                for detection in results.detections:
                    draw_glasses(image, detection)
                    # mp_drawing.draw_detection(image, detection)
            # Flip the image horizontally for a selfie-view display.
            writer.write(image)

            #cv2.imshow('MediaPipe Face Detection', cv2.flip(image, 1))
            if cv2.waitKey(15) & 0xFF == 27:
                break
    
    cap.release()
    writer.release()
