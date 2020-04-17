from copy import copy

import numpy as np
from tensorflow.contrib.specs.python import Reshape
from tensorflow.python.keras import Model
from tensorflow.python.keras.layers import Input, Dense, BatchNormalization


def autoencoder(input_shape=(9,9,11), min_layers=32, max_layers=512):
    output_shape      = copy(input_shape)
    output_shape[-1] -= 1

    x = inputs = Input(shape=input_shape)
    layers = max_layers
    while layers > min_layers:
        x = Dense(layers, activation='relu')(x)
        x = BatchNormalization()(x)
        layers = layers // 2

    x = Dense(min_layers, activation='relu')(x)
    x = BatchNormalization()(x)

    while layers <= max_layers:
        x = Dense(layers, activation='relu')(x)
        x = BatchNormalization()(x)
        layers = layers * 2

    outputs = Dense(np.prod(output_shape), activation='softmax')(x)
    outputs = Reshape(output_shape)(outputs)

    model   = Model(inputs, outputs, name='autoencoder')
    return model
