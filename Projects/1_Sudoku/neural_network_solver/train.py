#!/usr/bin/env python3
import tensorflow as tf
from tensorflow.python.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.python.keras.optimizers import Nadam

from neural_network_solver.dataset import dataset
from neural_network_solver.model import autoencoder

dataset_generator = dataset()

model = autoencoder()
model.compile(
    optimizer=Nadam(lr=0.001),
    loss=tf.keras.losses.categorical_crossentropy,
    metrics=['accuracy']
)

history = model.fit(
    dataset_generator,
    validation_split=0.2,
    batch_size=128,
    epochs=999,
    verbose=1,
    callbacks=[
        EarlyStopping(patience=8, verbose=1),
        ReduceLROnPlateau(patience=4, min_lr=1e-05),
        ModelCheckpoint(
            './neural_network_solver/models/autoencoder.hdfs',
            monitor='val_loss',
            verbose=False,
            save_best_only=True,
            save_weights_only=False,
            mode='auto',
        )
    ]
)