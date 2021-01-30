import json

from sklearn.cluster import DBSCAN


def load_json(json_path):
    with open(json_path, 'r') as json_:
        info = json.load(json_)
    return info


def clusterization_internal(vector_field, label_start_counter, vector_type, clustering_config):
    if not vector_field:
        return [], []
    data_for_cluster = []
    for item in vector_field:
        data_for_cluster.append([item["src_x"]])
    clustering = DBSCAN(eps=clustering_config.dbscan.eps, min_samples=clustering_config.dbscan.samples).fit(
        data_for_cluster)
    labels_ = clustering.labels_
    inf_for_drawing = []
    labels_new_numeration = []
    for label in labels_:
        if label == -1:
            labels_new_numeration.append(label)
        else:
            labels_new_numeration.append(label_start_counter + label)

    for i, item in enumerate(vector_field):
        inf_for_drawing.append({"dbscan_label": labels_new_numeration[i], **item, 'vector_type': vector_type})
    return inf_for_drawing, labels_new_numeration


def create_clusters_mask(labels, vectors_field):
    filter_vectors_field = []
    for i, label in enumerate(labels):
        if label != -1:
            filter_vectors_field.append(vectors_field[i])
    return filter_vectors_field
