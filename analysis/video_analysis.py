import json
import logging
import os

import cv2

from visualization.visualization import vector_draw, draw_info_with_clusters
from analysis.motions_vectors_analysis import analysis, vectors_clustering
from analysis.vectors_analysis import clusters_distribution_analysis, clusters_filtering


def load_json(json_path):
    with open(json_path, 'r') as json_:
        info = json.load(json_)
    return info


class FrameExtractor:
    def __init__(self, video_path, start_frame=None, end_frame=None):
        self.start_frame = start_frame
        self.video = cv2.VideoCapture(video_path)
        self.video_name = os.path.split(video_path)[-1]
        self.fps = int(self.video.get(cv2.CAP_PROP_FPS))
        self.frames_number = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        if not self.video.isOpened():
            raise ValueError('cannot open video')

        if self.start_frame is not None:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        else:
            self.start_frame = 0

        if end_frame is not None:
            self.end_frame = end_frame
        else:
            self.end_frame = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.cur_frame_no = self.start_frame - 1

    def read_frame(self):
        success, img = self.video.read()
        self.cur_frame_no += 1
        if not success or self.cur_frame_no > self.end_frame:
            return None
        return img


class VideoProcessing(FrameExtractor):
    def __init__(self, video_path, scenes, jsones_path, debug_dir, segmentation_config,
                 clusterization_config, start_frame=None,
                 end_frame=None, save_images=False):
        super().__init__(video_path, start_frame, end_frame)
        self.scenes = scenes
        self.jsones_path = jsones_path
        self.save_images = save_images
        self.debug_dir = debug_dir
        self.zoom_info = {}
        self.segmentation_config = segmentation_config
        self.clusterization_config = clusterization_config

    def processing(self, process_scenes_only=True):
        logging.info('start to collect resnet features')
        index_ = 0
        if process_scenes_only:
            next_segment_to_process = self.scenes[index_]
            next_segment_to_process_start = next_segment_to_process['start_scene']
            next_segment_to_process_end = next_segment_to_process['end_scene']

        while True:
            img = self.read_frame()
            if img is None:
                break
            if process_scenes_only:
                continue_condition = next_segment_to_process_start <= self.cur_frame_no <= next_segment_to_process_end
            else:
                continue_condition = True
            if continue_condition:
                self.frame_analysis(img)
            if process_scenes_only:
                if self.cur_frame_no > next_segment_to_process_end:
                    index_ += 1
                    try:
                        next_segment_to_process = self.scenes[index_]
                        next_segment_to_process_start = next_segment_to_process['start_scene']
                        next_segment_to_process_end = next_segment_to_process['end_scene']
                    except:
                        break
        return self.zoom_info

    def frame_analysis(self, curr_frame):

        curr_json_path = os.path.join(self.jsones_path, '{}.json'.format(self.cur_frame_no + 1))
        all_mv_vectors = load_json(curr_json_path)
        if not all_mv_vectors:
            logging.info('no vectors found at {} '.format(self.cur_frame_no))
            return
        grand_vectors, grandstands_mask, field_mask, players_mask = analysis(all_mv_vectors, curr_frame,
                                                                             self.segmentation_config)
        if self.save_images:
            cv2.imwrite(self.debug_dir + '/{}_grandstands_mask.png'.format(self.cur_frame_no),
                        grandstands_mask * 255)
            cv2.imwrite(self.debug_dir + '/{}_field_mask.png'.format(self.cur_frame_no), field_mask * 255)
            img_with_vectors = vector_draw(grand_vectors, curr_frame)
            cv2.imwrite(self.debug_dir + '/{}_orig_vectors_img.png'.format(self.cur_frame_no), img_with_vectors)
        # answer = vectors_distribution_analysis(grand_vectors, self.cur_frame_no)
        all_clusters = vectors_clustering(grand_vectors, self.clusterization_config)
        if self.save_images:
            draw_info_with_clusters(all_clusters, curr_frame, self.debug_dir, frame_no=self.cur_frame_no)
        filtered_clusters = clusters_filtering(all_clusters)
        zoom_info_current_frame = clusters_distribution_analysis(filtered_clusters, self.cur_frame_no)
        assert zoom_info_current_frame is not None
        self.zoom_info[self.cur_frame_no] = zoom_info_current_frame
        logging.debug('answer {} '.format(zoom_info_current_frame))
