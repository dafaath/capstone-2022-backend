import os
import pickle
from functools import lru_cache

import tensorflow as tf
from keras.preprocessing.text import Tokenizer


@lru_cache(maxsize=1)
def get_tokenizer():
    tokenizer = None
    filename = 'tokenizer.pickle'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'utils', filename)
    with open(full_path_filename, 'rb') as x:
        tokenizer: Tokenizer = pickle.load(x)
    return tokenizer


@lru_cache(maxsize=1)
def get_model():
    filename = 'model.h5'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'utils', filename)
    model = tf.keras.models.load_model(full_path_filename)
    return model
