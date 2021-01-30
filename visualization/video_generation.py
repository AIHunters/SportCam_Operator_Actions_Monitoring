import json
import logging
import os
import argparse
import cv2
from copy import deepcopy
from analysis.video_analysis import FrameExtractor
from analysis.meta_postprocessing import camera_motion_analysis_postprocessing


def draw_word(image, word):
    if word == 'left' or word == 'right':
        image = cv2.putText(image, word, (20, 25), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), thickness=2)
    elif word == 'zoom_in' or word == 'zoom_out':
        image = cv2.putText(image, word, (100, 25), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), thickness=2)
    return image


class VideoGenerationDescr(FrameExtractor):
    def __init__(self, video_path, imgs_save_path, json_info_path,
                 start_frame=None,
                 end_frame=None):
        super().__init__(video_path, start_frame, end_frame)
        self.imgs_save_path = imgs_save_path
        self.passed_frames_quantity = 0
        with open(json_info_path, 'r') as json___:
            self.json_info = json.load(json___)
        self.images_labels = {}
        self.images_loading(os.path.dirname(os.path.abspath(__file__)) + '/images')

    def put_single_image_on(self, image_we_put_on, image_we_put, position, delta=10, resize_constant=7):
        h, w, _ = image_we_put_on.shape
        h_small, w_small, _ = image_we_put.shape
        image_we_put = cv2.resize(image_we_put, (w_small // resize_constant, h_small // resize_constant))
        h_small, w_small, _ = image_we_put.shape

        if position == 'left':
            top_left = (delta, int(h / 2 - h_small / 2))
            bottom_right = (delta + w_small, int(h / 2 + h_small / 2))
        elif position == 'right':
            top_left = (w - w_small - delta, int(h / 2 - h_small / 2))
            bottom_right = (w - delta, int(h / 2 + h_small / 2))
        elif position == 'zoom_in':
            top_left = (int(w / 2 - w_small / 2), delta)
            bottom_right = (int(w / 2 + w_small / 2), delta + h_small)
        elif position == 'zoom_out':
            top_left = (int(w / 2 - w_small / 2), h - h_small - delta)
            bottom_right = (int(w / 2 + w_small / 2), h - delta)
        else:
            raise ValueError(
                'check you motion description, it should be "left ",  "right ",  "zoom_in " or  "zoom_out "')
        image_we_put_on[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = image_we_put
        return image_we_put_on

    def choose_labels_images_we_need(self, camera_motion_description):
        labels = {name: self.images_labels['white'][name] for name in self.images_labels['white'] if
                  name not in camera_motion_description}
        for label in camera_motion_description:
            labels[label] = self.images_labels['red'][label]
        return labels

    def put_images(self, img, camera_motion_description, alpha=0.4):
        img_with_labels = deepcopy(img)
        if camera_motion_description == ['None']:
            camera_motion_description = []
        labels_images_we_need = self.choose_labels_images_we_need(camera_motion_description)
        for label, img_label in labels_images_we_need.items():
            img_with_labels = self.put_single_image_on(img_with_labels, img_label, label)
        final_image = cv2.addWeighted(img, alpha, img_with_labels, (1 - alpha), 0.0)
        return final_image

    def images_loading(self, imgs_dir):
        folders_color = os.listdir(imgs_dir)
        for color in folders_color:
            self.images_labels[color] = {}
            imgs_names = os.listdir(os.path.join(imgs_dir, color))
            for single_img_name in imgs_names:
                curr_img_path = os.path.join(imgs_dir, color, single_img_name)
                self.images_labels[color][single_img_name[:-4]] = cv2.imread(curr_img_path)

    def image_meta_drawing(self, image, text):
        image_with_word = draw_word(image, text)
        return image_with_word

    def drawing(self):
        while True:
            img = self.read_frame()
            if img is None:
                logging.info('video stopped')
                break
            if str(self.cur_frame_no) in self.json_info:
                curr_frame_text = self.json_info[str(self.cur_frame_no)]
                if curr_frame_text == [None]:
                    curr_frame_text = []
                # image_with_info = self.image_meta_drawing(img, curr_frame_text)
                image_with_info = self.put_images(img, curr_frame_text)
                curr_image_path = os.path.join(self.imgs_save_path,
                                               '{:07d}.png'.format(self.cur_frame_no))
                cv2.imwrite(curr_image_path, image_with_info)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='custom arguments without using Sacred library ')
    parser.add_argument('--video_path',
                        default='/media/meshkovaki/34EC69CAF782C377/Datasets/sport/sport_demo_dataset/Football/video/Inter-Milan-vs-Juventus-2018-Full-Match-babak-2_360_240.mp4')
    parser.add_argument('--imgs_save_path',
                        default='/media/meshkovaki/34EC69CAF782C377/Projects/results/InterMilan_full_check__')
    parser.add_argument('--json_info_path', default='/media/meshkovaki/34EC69CAF782C377/Projects/answers.json')

    args = parser.parse_args()
    gen = VideoGenerationDescr(args.video_path, args.imgs_save_path, args.json_info_path)
    gen.drawing()
