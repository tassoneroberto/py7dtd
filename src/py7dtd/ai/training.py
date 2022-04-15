from imageai.Detection.Custom import DetectionModelTrainer

trainer = DetectionModelTrainer()
trainer.setModelTypeAsYOLOv3()
trainer.setDataDirectory(data_directory="ai/dataset")
trainer.setTrainConfig(
    object_names_array=["tree", "zombie"],
    batch_size=4,
    num_experiments=200,
    train_from_pretrained_model="ai/pretrained-yolov3.h5",
)
trainer.trainModel()
