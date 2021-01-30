import cv2
import numpy as np

from segmentation.region_growing_algorithm import Point, regionGrow


def image_segmentation(img, segmentation_config):
    h, w, _ = img.shape
    grid_size = segmentation_config.segmentation.grid_size
    threshold = segmentation_config.segmentation.threshold
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask_green = cv2.inRange(hsv, (36, 25, 25), (86, 255, 255))
    grid_mask_values = np.zeros((h // grid_size, w // grid_size))
    for i in range(h // grid_size):
        for j in range(w // grid_size):
            grid_cell_values = [mask_green[k][p] for k in range(i * grid_size, (i + 1) * grid_size) for p in
                                range(j * grid_size, (j + 1) * grid_size)]
            grid_mask_values[i][j] = sum(grid_cell_values) / len(grid_cell_values)
    h_grid, w_grid = grid_mask_values.shape
    seeds = [Point(0, 0), Point(w_grid - 1, 0), Point(0, h_grid - 1), Point(w_grid - 1, h_grid - 1)]
    binaryImg = regionGrow(grid_mask_values, seeds, threshold)
    grandstands_mask = binaryImg
    # remove bottom lines at the area below field
    h_, w_ = grandstands_mask.shape
    for col in range(w_):
        zero_coords = np.where(grandstands_mask[:, col] == 0)[0].tolist()
        if len(zero_coords) > 0:
            max_y_coord = np.max(zero_coords[0])
            for cell in range(max_y_coord, h_):
                grandstands_mask[cell, col] = 0

    binaryImg_inv = np.abs(binaryImg - 1)
    fileds_players = np.abs(binaryImg - 1)
    field_mask = cv2.bitwise_and(fileds_players, binaryImg_inv)
    field_mask_inv = np.abs(field_mask - 1)
    players_mask = cv2.bitwise_and(binaryImg_inv, field_mask_inv)
    grandstands_mask = cv2.resize(grandstands_mask, (w, h))
    return grandstands_mask, field_mask, players_mask
