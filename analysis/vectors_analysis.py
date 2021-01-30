import logging

import numpy as np


def clusters_distribution_analysis(clusters_info, frame_no):
    centers = {}
    current_types_of_clusters = list(clusters_info.keys())
    assert len(current_types_of_clusters) <= 3
    if not current_types_of_clusters:
        logging.info('camera is static !')
        print('camera {} is static !'.format(frame_no))
        return ['None']
    elif len(current_types_of_clusters) == 1:
        if current_types_of_clusters[0] == 'positive':
            return ['left']
        elif current_types_of_clusters[0] == 'negative':
            return ['right']
        else:  # current_types_of_clusters[0] == 'zero':
            logging.info('camera {} is static !'.format(frame_no))
            print('camera {} is static !'.format(frame_no))
            return ['None']
    else:  # length is 2 or 3 - zoom
        for type, labels in clusters_info.items():
            most_massive_cluster_ind = np.argmax([len(labels[label]) for label in labels])
            most_massive_cluster = list(labels.values())[most_massive_cluster_ind]
            curr_src_x = [cl['src_x'] for cl in most_massive_cluster]
            most_massive_cluster_center = np.median(curr_src_x, axis=0)
            centers[type] = most_massive_cluster_center

        centers_sorted = {k: v for k, v in sorted(centers.items(), key=lambda item: item[1])}
        names_sorted_clusters = list(centers_sorted.keys())
        if names_sorted_clusters[0] == 'negative':
            return ['zoom_in']
        elif names_sorted_clusters[0] == 'positive':
            return ['zoom_out']
        else:
            assert len(names_sorted_clusters) == 2  # red can be only in the middle if there is 3 clusters
            assert names_sorted_clusters[0] == 'zero'
            if names_sorted_clusters[-1] == 'negative':
                return ['zoom_out']
            elif names_sorted_clusters[-1] == 'positive':
                return ['zoom_in']


def clusters_filtering(all_info_about_clusters, trash_index=-1):
    types_clusters = {}
    for single_vector in all_info_about_clusters:
        if single_vector['dbscan_label'] == trash_index:
            continue
        if single_vector['vector_type'] not in types_clusters:
            types_clusters[single_vector['vector_type']] = {}
        if single_vector['dbscan_label'] not in types_clusters[single_vector['vector_type']]:
            types_clusters[single_vector['vector_type']][single_vector['dbscan_label']] = []
        types_clusters[single_vector['vector_type']][single_vector['dbscan_label']].append(single_vector)
    return types_clusters
