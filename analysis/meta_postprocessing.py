# сейчас всегда добавляется + гэп так как вовремя не обновляется длина

def fill_in_necessary_labels(info, frames_to_connect):
    key_type = type(list(info.keys())[0])

    for label, label_frames in frames_to_connect.items():
        for single_frames_pair in label_frames:
            for frame_no_to_fill_in in range(single_frames_pair[0], single_frames_pair[1] + 1):
                key_we_get = key_type(frame_no_to_fill_in)
                if key_we_get not in info:
                    continue
                assert label not in info[key_we_get]
                if info[key_we_get] == [None]:
                    info[key_we_get] = []
                info[key_we_get].append(label)
    return info


def find_labels_segments(info):
    segments = {}
    info_len = len(list(info.keys()))
    for index, (frame_no, frame_info_list) in enumerate(info.items()):
        assert len(frame_info_list) == 1
        frame_info = frame_info_list[0]
        frame_no = int(frame_no)
        if index == info_len - 1:
            for key, value in segments.items():
                if 'end' not in value[-1]:
                    segments[key][-1]['end'] = frame_no - 1
        else:
            if frame_info not in segments:
                segments[frame_info] = []
                segments[frame_info].append({'start': frame_no})
                without_end_keys = [key for key in segments if key != frame_info and 'end' not in segments[key][-1]]
                for key in without_end_keys:
                    segments[key][-1]['end'] = frame_no - 1
                continue
            without_end_keys = [key for key in segments if 'end' not in segments[key][-1]]

            if frame_info in without_end_keys:
                without_end_keys_filtered = [f for f in without_end_keys if f != frame_info]
                for key in without_end_keys_filtered:
                    segments[key][-1]['end'] = frame_no - 1
            else:
                segments[frame_info].append({'start': frame_no})
                for key in without_end_keys:
                    segments[key][-1]['end'] = frame_no - 1
    return segments


def find_frames_number_to_fill_labels_in(segments, min_gap_to_connect):
    frames_to_connect = {}
    for key, values in segments.items():
        if key not in frames_to_connect:
            frames_to_connect[key] = []
        for segments_index in range(0, len(values) - 2):
            if values[segments_index + 1]['start'] - values[segments_index]['end'] <= min_gap_to_connect:
                frames_to_connect[key].append(
                    [values[segments_index]['end'] + 1, values[segments_index + 1]['start'] - 1])
            else:
                if values[segments_index]['end'] - values[segments_index]['start'] <= min_gap_to_connect:
                    frames_to_connect[key].append(
                        [values[segments_index]['end'] + 1, values[segments_index]['end'] + min_gap_to_connect])
    return frames_to_connect


def find_frames_number_to_fill_labels_in_groups_considering(segments, min_gap_to_connect,
                                                            groups_to_consider=None):
    if groups_to_consider is None:
        groups_to_consider = [['left', 'right'], ['zoom_in', 'zoom_out']]
    frames_to_connect = {}
    for group in groups_to_consider:
        segments_group = [[[i, k] for i in segments[k]] for k in group]
        segments_group = [item for sublist in segments_group for item in sublist]
        segments_group.sort(key=lambda x: x[0]['start'])
        for key_single in group:
            frames_to_connect[key_single] = []

        for segments_index in range(0, len(segments_group) - 2):
            key_curr = segments_group[segments_index][1]
            if segments_group[segments_index + 1][0]['start'] - segments_group[segments_index][0][
                'end'] <= min_gap_to_connect:
                frames_to_connect[key_curr].append(
                    [segments_group[segments_index][0]['end'] + 1, segments_group[segments_index + 1][0]['start'] - 1])
            else:
                if segments_group[segments_index][0]['end'] - segments_group[segments_index][0][
                    'start'] <= min_gap_to_connect:
                    frames_to_connect[key_curr].append(
                        [segments_group[segments_index][0]['end'] + 1,
                         segments_group[segments_index][0]['end'] + min_gap_to_connect])

    return frames_to_connect


def fill_in_static_frames(info):
    info_keys = list(info.keys())
    for index, (single_frame, frame_info) in enumerate(info.items()):
        if index == 0:
            if frame_info == ['static']:
                info[single_frame] = [None]
            continue
        if frame_info == ['static']:
            info[single_frame] = info[info_keys[index - 1]]
    return info


def find_short_segments(segments, min_len):
    segments_to_delete = []
    filtered_segments_left = {}
    for name, segments_values in segments.items():
        if name is None:
            continue
        if name not in filtered_segments_left:
            filtered_segments_left[name] = []
        for single_segment in segments_values:
            if single_segment['end'] - single_segment['start'] + 1 <= min_len:
                segments_to_delete.append({'time': [single_segment['start'], single_segment['end']], 'name': name})
            else:
                filtered_segments_left[name].append(single_segment)
    return segments_to_delete, filtered_segments_left


def remove_short_segments(info, segments_to_delete):
    for segment_ in segments_to_delete:
        for frame_no in range(segment_['time'][0], segment_['time'][1] + 1):
            if len(info[frame_no]) == 1:
                info[frame_no] = [None]
            else:
                info[frame_no].remove(segment_['name'])
    return info


def camera_motion_analysis_postprocessing(info, postprocessing_params):
    segments = find_labels_segments(info)
    frames_to_connect = find_frames_number_to_fill_labels_in_groups_considering(segments,
                                                                                postprocessing_params.min_gap_to_connect)
    filled_info = fill_in_necessary_labels(info, frames_to_connect)
    return filled_info
