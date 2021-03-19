import sys
import numpy as np
import cv2
import os
from PIL import ImageDraw, Image

def update_rect_adapt_landmark(INPUT_H, INPUT_W, h, w, bbox, lmk):
    r_w = INPUT_W / (w * 1.0)
    r_h = INPUT_H / (h * 1.0)
    if (r_h > r_w) :
        l = bbox[0] / r_w
        r = bbox[2] / r_w
        t = (bbox[1] - (INPUT_H - r_w * h) / 2) / r_w
        b = (bbox[3] - (INPUT_H - r_w * h) / 2) / r_w
        for i in range(0, 10, 2):
            lmk[i] /= r_w
            lmk[i + 1] = (lmk[i + 1] - (INPUT_H - r_w * h) / 2) / r_w
    else :
        l = (bbox[0] - (INPUT_W - r_h * w) / 2) / r_h
        r = (bbox[2] - (INPUT_W - r_h * w) / 2) / r_h
        t = bbox[1] / r_h
        b = bbox[3] / r_h
        for i in range(0, 10, 2):
            lmk[i] = (lmk[i] - (INPUT_W - r_h * w) / 2) / r_h
            lmk[i + 1] /= r_h
    bbox[0] = l
    bbox[1] = t
    bbox[2] = r - l
    bbox[3] = b - t

def draw_keypoints(img, box, face_landmarks):
    box = [int(b) for b in box]
    face_landmarks = [int(x) for x in face_landmarks]

    point_size = 3
    point_color = (0, 255, 0) # BGR
    thickness = -1
    # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    for i in range(0, len(face_landmarks), 2):
        point = (face_landmarks[i], face_landmarks[i+1])
        # cv2.circle(img, point, point_size, point_color, thickness)
    red = (0, 0, 255)
    cv2.rectangle(img, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), red, 2)

def draw_a_box(img, box):
    box = [int(b) for b in box]
    red = (0, 0, 255)
    cv2.rectangle(img, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), red, 2)

def image2str(image):
    image_jpg = cv2.imencode('.bmp', image)[1]
    image_str = image_jpg.tostring()
    return image_str

def str2image(image_str):
    # image_jpg = np.fromstring(image_str, np.uint8)
    image_jpg = np.frombuffer(image_str, np.uint8)
    image = cv2.imdecode(image_jpg, cv2.IMREAD_COLOR)
    return image

# https://blog.csdn.net/a6831115/article/details/101142188
def is_rotate_image(img_file):
    try:
        image = Image.open(img_file)
    except:
        print (img_file, ', open fail')
        return None
    is_rotated  = False
    try :
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' :
                break

        if img_file.split('.')[-1] == 'png':
            image = open(img_file,'rb')
            Info = exifread.process_file(image)
        elif img_file.split('.')[-1] == 'jpg' or img_file.split('.')[-1] == 'jpeg':
            image = Image.open(img_file)
            Info = image._getexif()
        else:
            Info = None

        if Info:
            exif=dict(Info.items())
            val = exif.get(orientation, -1)
            if val == 3 :
                is_rotated = True
                image=image.rotate(180, expand=True)
            elif val == 6 :
                is_rotated = True
                image=image.rotate(270, expand=True)
            elif val == 8 :
                is_rotated = True
                image=image.rotate(90, expand=True)

        if is_rotated:
            if not os.path.exists("rotated_image"):
                os.mkdir("rotated_image")
            rotated_img_file = os.path.join("rotated_image", os.path.basename(img_file))
            # print ("rotated_img_file:", rotated_img_file)
            image.save(rotated_img_file)
    except:
        print("err_info:\n%s" % traceback.format_exc())
        return img_file

    if is_rotated:
        return rotated_img_file
    else:
        return img_file


def letter_box_image(image: Image.Image, output_height: int, output_width: int, fill_value)-> np.ndarray:
    """
    Fit image with final image with output_width and output_height.
    :param image: PILLOW Image object.
    :param output_height: width of the final image.
    :param output_width: height of the final image.
    :param fill_value: fill value for empty area. Can be uint8 or np.ndarray
    :return: numpy image fit within letterbox. dtype=uint8, shape=(output_height, output_width)
    """

    height_ratio = float(output_height)/image.size[1]
    width_ratio = float(output_width)/image.size[0]
    fit_ratio = min(width_ratio, height_ratio)
    fit_height = int(image.size[1] * fit_ratio)
    fit_width = int(image.size[0] * fit_ratio)
    fit_image = np.asarray(image.resize((fit_width, fit_height), resample=Image.BILINEAR))

    if isinstance(fill_value, int):
        fill_value = np.full(fit_image.shape[2], fill_value, fit_image.dtype)

    to_return = np.tile(fill_value, (output_height, output_width, 1))
    pad_top = int(0.5 * (output_height - fit_height))
    pad_left = int(0.5 * (output_width - fit_width))
    to_return[pad_top:pad_top+fit_height, pad_left:pad_left+fit_width] = fit_image
    return to_return


def convert_to_original_size(box, size, original_size, is_letter_box_image):
    if is_letter_box_image:
        box = box.reshape(2, 2)
        box[0, :] = letter_box_pos_to_original_pos(box[0, :], size, original_size)
        box[1, :] = letter_box_pos_to_original_pos(box[1, :], size, original_size)
    else:
        ratio = original_size / size
        box = box.reshape(2, 2) * ratio
    return list(box.reshape(-1))


def letter_box_pos_to_original_pos(letter_pos, current_size, ori_image_size)-> np.ndarray:
    """
    Parameters should have same shape and dimension space. (Width, Height) or (Height, Width)
    :param letter_pos: The current position within letterbox image including fill value area.
    :param current_size: The size of whole image including fill value area.
    :param ori_image_size: The size of image before being letter boxed.
    :return:
    """
    letter_pos = np.asarray(letter_pos, dtype=np.float)
    current_size = np.asarray(current_size, dtype=np.float)
    ori_image_size = np.asarray(ori_image_size, dtype=np.float)
    final_ratio = min(current_size[0]/ori_image_size[0], current_size[1]/ori_image_size[1])
    pad = 0.5 * (current_size - final_ratio * ori_image_size)
    pad = pad.astype(np.int32)
    to_return_pos = (letter_pos - pad) / final_ratio
    return to_return_pos


def draw_boxes(boxes, img, cls_names, detection_size, is_letter_box_image):
    draw = ImageDraw.Draw(img)

    for cls, bboxs in boxes.items():
        color = tuple(np.random.randint(0, 256, 3))
        for box, score in bboxs:
            box = convert_to_original_size(box, np.array(detection_size),
                                           np.array(img.size),
                                           is_letter_box_image)
            draw.rectangle(box, outline=color)
            draw.text(box[:2], '{} {:.2f}%'.format(cls_names[cls], score * 100), fill=color)