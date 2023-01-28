#!/usr/bin/env python3

import argparse
import os

from imageai.Detection.Custom import DetectionModelTrainer


class ModelTraining(object):
    def __init__(self, args):
        self.args = args

    def train(self) -> None:
        trainer = DetectionModelTrainer()
        trainer.setModelTypeAsYOLOv3()
        trainer.setDataDirectory(data_directory=self.args.dataset)

        classes_file = open(
            os.path.join(self.args.dataset, "train/annotations/classes.txt"),
            "r",
        )
        entities = [
            line.strip()
            for line in classes_file.readlines()
            if line.strip() != ""
        ]
        classes_file.close()

        trainer.setTrainConfig(
            object_names_array=entities,
            batch_size=4,
            num_experiments=self.args.epochs,
            train_from_pretrained_model=self.args.pretrained,
        )

        trainer.trainModel()


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="./dataset",
        help="Dataset folder path",
        type=str,
    )
    parser.add_argument(
        "--pretrained",
        default="./dataset/models/yolov3.pt",
        help="Pre-trained model path",
        type=str,
    )
    parser.add_argument(
        "--epochs",
        default=200,
        help="Number of epochs to train",
        type=int,
    )

    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    model_training = ModelTraining(args)

    model_training.train()


if __name__ == "__main__":
    main()
