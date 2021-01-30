from copy import deepcopy

import cv2
import numpy as np


def draw_info_with_clusters(info_for_drawing, img, save_dir, frame_no):
    clusters = {-1: (255, 255, 255)}
    clusters_x_coordinate = {-1: []}
    clusters_y_coordinate = {-1: []}
    img_with_labels = deepcopy(img)
    labels = []
    for vector in info_for_drawing:
        if vector["dbscan_label"] not in labels:
            labels.append(vector["dbscan_label"])
        if vector["dbscan_label"] in clusters.keys():
            color = clusters[vector["dbscan_label"]]
        else:
            color = np.random.randint(0, 255, size=(3,))
            clusters[vector["dbscan_label"]] = color
            clusters_y_coordinate[vector["dbscan_label"]] = []
            clusters_x_coordinate[vector["dbscan_label"]] = []

        clusters_x_coordinate[vector["dbscan_label"]].append(vector["src_x"])
        clusters_y_coordinate[vector["dbscan_label"]].append(vector["src_y"])
        color = (int(color[0]), int(color[1]), int(color[2]))
        img_with_labels = cv2.line(img_with_labels, (vector['src_x'], vector['src_y']),
                                   (vector['dst_x'], vector['dst_y']),
                                   thickness=2,
                                   color=tuple(color))
    img_with_labels = cv2.circle(img_with_labels, (160, 90), 5, (0, 0, 0), -1)
    for label, cluster_color in clusters.items():
        if label == -1:
            continue
        center_x = np.median(clusters_x_coordinate[label])
        center_y = np.median(clusters_y_coordinate[label])
        color = (int(cluster_color[0]), int(cluster_color[1]), int(cluster_color[2]))

        img_with_labels = cv2.circle(img_with_labels, (int(center_x), int(center_y)), 5, color, -1)
    cv2.putText(img_with_labels, '{}'.format(labels), (20, 20), color=(255, 255, 255), thickness=2,
                fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1)
    cv2.imwrite(save_dir + '/{}_clusters.png'.format(frame_no),
                img_with_labels)


def vector_draw(vectors, image):
    for vector in vectors:
        if vector['dx'] > 0:
            color = (255, 0, 0)
        elif vector['dx'] < 0:
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)
        cv2.line(image, (vector['src_x'], vector['src_y']), (vector['dst_x'], vector['dst_y']), thickness=2,
                 color=color)
    return image
