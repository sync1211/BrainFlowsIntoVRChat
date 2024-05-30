import tensorflow as tf
import keras

from keras.models import Sequential
from keras.layers import Dense, MaxPooling1D, Activation, Flatten, Layer, Multiply, BatchNormalization, Dropout
from keras.layers import SeparableConv1D, Conv1D, UpSampling1D, Conv1DTranspose, UpSampling1D, AveragePooling1D, GlobalAveragePooling1D

## Spatial Attention (Thanks Summer!)
@keras.saving.register_keras_serializable()
class SpatialAttention(Layer):
    def __init__(self, kernel_size=7, **kwargs):
        super(SpatialAttention, self).__init__(**kwargs)
        self.kernel_size = kernel_size
        self.conv = Conv1D(1, self.kernel_size, padding='same', activation='sigmoid', use_bias=False)
    
    def call(self, inputs):
        avg_out = tf.reduce_mean(inputs, axis=-1, keepdims=True)
        max_out = tf.reduce_max(inputs, axis=-1, keepdims=True)
        x = tf.concat([avg_out, max_out], axis=2)
        x = self.conv(x)
        return Multiply()([inputs, x])

## Encoder and Decoder Trained on the physionet motor imagery dataset
## https://www.physionet.org/content/eegmmidb/1.0.0/
## Thanks again to Summer, Programmerboi, Hosomi

act = 'silu'

encoder = Sequential([ 
    SeparableConv1D(128, 3, padding='same'),
    BatchNormalization(), Activation(act), MaxPooling1D(2),
    SeparableConv1D(64, 3, padding='same'),
    BatchNormalization(), Activation(act), MaxPooling1D(2),
    SeparableConv1D(32, 3, padding='same'),
    Activation(act)
])

decoder = Sequential([
    SeparableConv1D(32, 3, padding='same'), 
    BatchNormalization(), Activation(act), UpSampling1D(2),
    SeparableConv1D(64, 3, padding='same'), 
    BatchNormalization(), Activation(act), UpSampling1D(2),
    SeparableConv1D(128, 3, padding='same'),
    BatchNormalization(), Activation(act),

    SeparableConv1D(64, 1, padding='same', activation='sigmoid'),
])

## First Layer to convert any channels to 64 ranged [0, 1]
def create_first_layer(channels):
    return Sequential([
        Conv1D(64, channels, padding='same'),
        BatchNormalization(),
        Activation('sigmoid'),
    ])

## Last Layer to map latent space to custom classes
def create_last_layer(classes):
    return Sequential([
        BatchNormalization(),
        GlobalAveragePooling1D(),
        Dropout(0.1),
        Dense(classes, activation='softmax')
    ])