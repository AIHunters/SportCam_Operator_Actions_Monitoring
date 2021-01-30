import json

from analysis.meta_postprocessing import camera_motion_analysis_postprocessing
from analysis.video_analysis import VideoProcessing


def main(video_path, scenes_json, jsones_path, debug_images_dir, save_images, config_params_analysis,
         config_params_clusterization, config_params_segmentation):
    if scenes_json is not None:
        with open(scenes_json, 'r') as json___:
            scenes = json.load(json___)
        scenes_gates = [scene for scene in scenes if
                        scene['label_scene'] == config_params_analysis.scenes_filtration.label]
        if config_params_analysis.scenes_filtration.start is not None and config_params_analysis.scenes_filtration.end is not None:
            scenes_gates = [scene for scene in scenes_gates if config_params_analysis.scenes_filtration.start <= scene[
                'start_scene'] <= config_params_analysis.scenes_filtration.end]
        process_scenes_only = True
    else:
        scenes_gates = None
        process_scenes_only = False

    processor = VideoProcessing(video_path, scenes_gates, jsones_path, debug_images_dir, config_params_segmentation,
                                config_params_clusterization, save_images=save_images)
    camera_movement_description = processor.processing(process_scenes_only)
    if config_params_analysis.postprocessing.mode == 'on':
        camera_movement_description = camera_motion_analysis_postprocessing(camera_movement_description,
                                                                            config_params_analysis.camera_motion_analysis_postprocessing)
    return camera_movement_description
