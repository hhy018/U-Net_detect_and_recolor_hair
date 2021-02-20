import time
import cv2
import keras
import numpy as np
import os
from scipy.misc import imread, imresize, imsave
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
def predict(model, im):
    h, w, _ = im.shape
    inputs = cv2.resize(im, (480, 480))
    inputs = inputs.astype('float32')
    inputs.shape = (1,) + inputs.shape
    inputs = inputs / 255
    mask = model.predict(inputs)
    # ret, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY_INV)
    mask.shape = mask.shape[1:]
    mask = cv2.resize(mask, (w, h))
    mask.shape = h, w, 1
    return mask


def change_v(v, mask, target):
    # 染发
    epsilon = 1e-7
    x = v / 255                             # 数学化
    target = target / 255
    target = -np.log(epsilon + 1 - target)
    x_mean = np.sum(-np.log(epsilon + 1 - x)  * mask) / np.sum(mask)
    alpha = target / x_mean
    x = 1 - (1 - x) ** alpha
    v[:] = x * 255                          # 二进制化


def recolor(im, mask, color=(0x40, 0x16, 0x66)):
    # 工程化
    print("color1:", color)
    print("type of color 1:", type(color))
    color = np.array(color, dtype='uint8', ndmin=3)
    print("color2:", color)
    print("type of color 2:", type(color))
    im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    color_hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    # 染发
    im_hsv[..., 0] = color_hsv[..., 0]      # 修改颜色
    change_v(im_hsv[..., 2:], mask, color_hsv[..., 2:])
    im_hsv[..., 1] = color_hsv[..., 1]      # 修改饱和度
    x = cv2.cvtColor(im_hsv, cv2.COLOR_HSV2BGR)
    im = im * (1 - mask) + x * mask
    return im

###########图片处理
def SolveImage(model, color=(0x40, 0x16, 0x66)):
    imgs = [f for f in os.listdir('./imgs/test')]
    for na in imgs:
        im = imread(os.path.join('./imgs/test', na), mode='RGB')
        start = time.perf_counter()
        mask = predict(model, im)
        print(time.perf_counter() - start)
        start = time.perf_counter()
        im = recolor(im, mask, color)
        print(time.perf_counter() - start)
        # cv2.imwrite('mask.jpg', mask * 255)
        imsave('imgs/results/' + na, im)
        cv2.imshow('result', im)
        cv2.waitKey(0)
##摄像头
def SolveCapter(model, color=(0x40, 0x16, 0x66)):
    capture = cv2.VideoCapture(0)
    capture.set(3, 640)  # 设置分辨率
    capture.set(4, 480)
    while (True):
        ret, im = capture.read( )
        # im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
        cv2.imshow('src', im )

        mask = predict(model, im)
        start = time.perf_counter()
        im2 = recolor(im, mask, color)
        print(time.perf_counter() - start)

        im_save = cv2.cvtColor(im2, cv2.COLOR_BGR2RGB)
        imsave('imgs/results/1.jpg', im_save)
        # 进行类型转换 才可以显示
        im_sw = im2.astype(np.uint8)
        cv2.imshow('result', im_sw)

        if cv2.waitKey(20) == ord('q'):
           break
    capture.release()  # 释放ideoCapture对象
    cv2.destroyAllWindows()  # 释放视频播放窗口

def main(model,   color=(0x40, 0x16, 0x66)):
    # model模型位置， ifn 原图， ofn 处理结果图， （考虑将color设置为含参数路由）
    if isinstance(model, str):
        model = keras.models.load_model(model, compile=False)

    #SolveImage(model,color)
    SolveCapter(model,color)



if __name__ == '__main__':
    # data = np.load('../celeba.npz')
    # images, masks = data['images'], data['masks']
    # cv2.imwrite('celeba.image.123.jpg', images[123])
    # cv2.imwrite('celeba.mark.123.jpg', masks[123])

    main('weights.005.h5',  color=(200,200,200))
