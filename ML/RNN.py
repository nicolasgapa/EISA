"""
2020
Embry-Riddle Aeronautical University
Department of Physics and Life Sciences

Code developer: Nicolas Gachancipa

Embry-Riddle Ionospheric Algorithm (EISA) 2.0
Machine Learning (ML) for atmospheric data analysis
Recurrent Neural Networks (RNNs)

"""
# Imports
from keras.utils import np_utils
import numpy as np
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import tensorflow.keras as k

filesep = os.sep  # File separator (Changes between windows, linux and other OS).


# Class.
class RNNModel:

    def __init__(self, weights, load_weights=False):
        # Set weights.
        self.weights = weights

        # Neural network.
        self.network = k.models.Sequential([k.layers.Dense(units=20, activation='relu', input_shape=(None, 4)),
                                            k.layers.LSTM(64, return_sequences=True),
                                            k.layers.LSTM(64, return_sequences=True),
                                            k.layers.Dense(30, activation="relu"),
                                            k.layers.Dense(10, activation="relu"),
                                            k.layers.Dense(units=4, activation='softmax')])

        # Load weights (if applicable).
        if load_weights:
            self.network.load_weights(self.weights)

    def train(self, training_file, load_weights=False, optimizer='adam', loss='categorical_crossentropy', epochs=100,
              batch_size=100):
        # Print status.
        print('Training using: {}.'.format(training_file))

        # Get training data.
        df = pd.read_csv(training_file)
        X = df.drop("y", axis=1)
        X = np.asarray(X).astype('float32')
        X = np.expand_dims(X, axis=0)
        y = df["y"]

        # Encode class values as integers.
        encoder = LabelEncoder()
        encoder.fit(y)
        encoded_Y = encoder.transform(y)

        # Convert integers to dummy variables (i.e. one hot encoded).
        y = np_utils.to_categorical(encoded_Y)
        y = np.expand_dims(y, axis=0)

        # Compile and fit.
        if load_weights:
            self.network.load_weights(self.weights)
        self.network.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
        self.network.fit(X, y, epochs=epochs, batch_size=batch_size)
        self.weights = 'output_' + self.weights
        self.network.save_weights(self.weights)

    def detect(self, instance):
        # Event detection.
        return list(self.network.predict(instance)[0])


# Run ML.
def run_ML(input_file, output_file, weights):
    # Read data.
    X = pd.read_csv(input_file)

    # Extract columns.
    GPS_TOW = X['GPS TOW']
    X = X[['Elevation', 'CNo', 'S4', 'S4 Cor']]

    # Create RNN model.
    ML_model = RNNModel(weights, load_weights=True)

    # Detect scintillation.
    y = ML_model.detect(X)

    # Add GPS TOW and y to the data frame.
    X['GPS TOW'] = GPS_TOW
    X['y'] = y

    # Obtain the times when a scintillation event was identified.
    df = X[X['y'] > 0]

    # Save scintillation events to a new file (Only if an event was detected).
    if len(df) > 0:
        df.to_csv(output_file)
