import cv2
import os
import argparse


def video_collection_f(path_to_imgs, save_path, fps=25):
    video_name = os.path.split(path_to_imgs)[-1]
    imgs_names = sorted(os.listdir(path_to_imgs))
    imgs = []
    for index, img_name in enumerate(imgs_names):
        path_to_img = os.path.join(path_to_imgs, img_name)
        img = cv2.imread(path_to_img)
        height, width, layers = img.shape
        size = (width, height)
        imgs.append(img)
    out = cv2.VideoWriter(os.path.join(save_path, '{}.mp4'.format(video_name)), cv2.VideoWriter_fourcc(*'DIVX'),
                          fps,
                          size)

    for i in range(len(imgs)):
        out.write(imgs[i])
    out.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='custom arguments without using Sacred library ')
    parser.add_argument('--path_to_imgs',
                        default='/media/meshkovaki/34EC69CAF782C377/Datasets/sport/sport_demo_dataset/Football/video (1)/Real_Madrid_Sevilla_7_3_2013_360_imgs')
    parser.add_argument('--save_path', default='/media/meshkovaki/34EC69CAF782C377/Datasets/sport/sport_demo_dataset/Football/video (1)')

    args = parser.parse_args()
    video_collection_f(args.path_to_imgs, args.save_path)
