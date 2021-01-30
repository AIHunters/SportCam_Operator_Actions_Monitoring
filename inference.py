import json
import logging
import os

from visualization.video_creation import video_collection_f
from visualization.video_generation import VideoGenerationDescr

from analysis.config.config import Config as Config_analysis
from clusterization.config.config import Config as Config_clusterization
from main import main
from segmentation.config.config import Config as Config_segmentation


def full_pipeline(path_to_current_video, save_dir, path_to_motion_vectors, path_to_current_scenes_json,
                  debug_images_dir_name, config_params_analysis, config_params_clusterization,
                  config_params_segmentation, videos_path_good_quality=None, save_images=False):
    if save_dir is None:
        save_dir = os.path.join(os.path.abspath(os.getcwd()), 'results')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    if debug_images_dir_name is None:
        debug_images_dir_name = os.path.join(save_dir, 'images')
        if not os.path.exists(debug_images_dir_name):
            os.makedirs(debug_images_dir_name)
    video_name = os.path.split(path_to_current_video)[-1]
    camera_movement_description_folder = os.path.join(save_dir, video_name)
    if not os.path.exists(camera_movement_description_folder):
        os.makedirs(camera_movement_description_folder)
    debug_images_dir = os.path.join(camera_movement_description_folder, debug_images_dir_name)
    if not os.path.exists(debug_images_dir):
        os.makedirs(debug_images_dir)
    log_filename = camera_movement_description_folder + '/_log_res.log'
    if os.path.exists(log_filename):
        os.remove(log_filename)
    logging.basicConfig(level=logging.DEBUG, filename=log_filename)
    camera_movement_description = main(path_to_current_video, path_to_current_scenes_json, path_to_motion_vectors,
                                       debug_images_dir, save_images, config_params_analysis,
                                       config_params_clusterization, config_params_segmentation)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    name = 'camera_movement_description'
    json_path = os.path.join(camera_movement_description_folder, '{}.json'.format(name))
    with open(json_path, 'w') as json_file:
        json.dump(camera_movement_description, json_file, indent=4)

    imgs_save_dir = os.path.join(camera_movement_description_folder, '{}'.format(video_name))
    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)

    path_to_video_to_draw_on = path_to_current_video if videos_path_good_quality is None else os.path.join(
        videos_path_good_quality, video_name)
    gen = VideoGenerationDescr(path_to_video_to_draw_on, imgs_save_dir, json_path)
    gen.drawing()
    video_collection_f(imgs_save_dir, camera_movement_description_folder)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--video_path", )
    parser.add_argument("--videos_path_good_quality",
                        default=None)
    parser.add_argument("--save_dir", default=None)
    parser.add_argument("--path_to_scenes_json", default=None)
    parser.add_argument("--path_to_motion_vectors",
                        default='/media/meshkovaki/34EC69CAF782C377/Projects/motion_vectors/MV-Tractus/output/Real_Madrid_Sevilla_7_3_2013_360_imgs')
    parser.add_argument("--save_images",
                        default=False)
    parser.add_argument("--debug_images_dir", default=None)
    args = parser.parse_args()

    config_params_clusterization = Config_clusterization()
    config_params_clusterization.load('./clusterization/config.yml')

    config_params_analysis = Config_analysis()
    config_params_analysis.load('./analysis/config.yml')

    config_params_segmentation = Config_segmentation()
    config_params_segmentation.load('./segmentation/config.yml')

    full_pipeline(args.video_path, args.save_dir, args.path_to_motion_vectors, args.path_to_scenes_json,
                  args.debug_images_dir, config_params_analysis, config_params_clusterization,
                  config_params_segmentation,
                  videos_path_good_quality=args.videos_path_good_quality, save_images=args.save_images)
