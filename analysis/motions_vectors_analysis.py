import logging

from clusterization.clustering import clusterization_internal
from segmentation.segmentation import *


def filter_vectors_by_mask_dict(vectors, mask_indices):
    # for simplicity we just consider the beginning and the end of vector
    filtered_vectors = []
    for index, vector in enumerate(vectors):
        if vector['src_y'] in mask_indices and vector['dst_y'] in mask_indices:
            if vector['src_x'] in mask_indices[vector['src_y']] and vector['dst_x'] in mask_indices[vector['dst_y']]:
                filtered_vectors.append(vector)
    return filtered_vectors


def analysis(curr_frame_motion_vectors, img, segmentation_parameters):
    grandstands_mask, field_mask, players_mask = image_segmentation(img, segmentation_parameters)

    grandstands_mask_indices = np.where(grandstands_mask == 1.)
    grandstands_mask_indices_dict = {i: [] for i in set(list(grandstands_mask_indices[0]))}
    for i, j in zip(grandstands_mask_indices[0], grandstands_mask_indices[1]):
        grandstands_mask_indices_dict[i].append(j)
    grandstands_vectors = filter_vectors_by_mask_dict(curr_frame_motion_vectors, grandstands_mask_indices_dict)

    return grandstands_vectors, grandstands_mask, field_mask, players_mask


def split_vectors_by_sign(vectors):
    neg_vectors_dx = []
    pos_vectors_dx = []
    zero_vectors_dx = []
    for vector in vectors:
        if vector['dx'] > 0:
            pos_vectors_dx.append(vector)
        elif vector['dx'] < 0:
            neg_vectors_dx.append(vector)
        else:
            zero_vectors_dx.append(vector)
    return pos_vectors_dx, neg_vectors_dx, zero_vectors_dx


def vectors_clustering(curr_frame_motion_vectors, clusterization_config):
    pos_vectors_dx, neg_vectors_dx, zero_vectors_dx = split_vectors_by_sign(curr_frame_motion_vectors)
    label_start = 0
    inf_for_drawing_pos, labels_pos = clusterization_internal(pos_vectors_dx, label_start, 'positive',
                                                              clusterization_config)
    label_start_pos = len(set(labels_pos).difference({-1})) + 1

    inf_for_drawing_neg, labels_neg = clusterization_internal(neg_vectors_dx, label_start_pos, 'negative',
                                                              clusterization_config)
    label_start_neg = len(set(labels_neg).difference({-1})) + label_start_pos + 1

    inf_for_drawing_zero, labels_zero = clusterization_internal(zero_vectors_dx, label_start_neg, 'zero',
                                                                clusterization_config)
    logging.debug("DBSCAN clusters: {}".format(np.unique(labels_pos + labels_neg + labels_zero)))
    inf_all = inf_for_drawing_pos + inf_for_drawing_zero + inf_for_drawing_neg
    return inf_all
