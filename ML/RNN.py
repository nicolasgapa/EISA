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
from Graphing.support_graphing_functions import time_ranges
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
import numpy as np
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from ML.support_ML_functions import plot_scintillation_detections
import tensorflow.keras as k

filesep = os.sep  # File separator (Changes between windows, linux and other OS).


# Class.
class RNNModel:

    def __init__(self, weights, load_weights=False):
        # Set weights.
        self.weights = weights

        # Neural network.
        self.network = k.models.Sequential([k.layers.Dense(units=20, activation='relu', input_shape=(None, 4)),
                                            # k.layers.LSTM(64, return_sequences=True),
                                            # k.layers.LSTM(64, return_sequences=True),
                                            # k.layers.Dense(30, activation="relu"),
                                            k.layers.Dense(10, activation="relu"),
                                            k.layers.Dense(units=5, activation='softmax')])

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

        # Checkpoint.
        weights_file = os.path.dirname(self.weights) + '\\checkpoint' + os.path.basename(self.weights)
        checkpoint = ModelCheckpoint(weights_file, verbose=1, monitor='loss',
                                     save_best_only=True, mode='auto')

        # Compile and fit.
        if load_weights:
            self.network.load_weights(self.weights)
        self.network.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
        self.network.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=[checkpoint])

        # Save weights (overrides the original weights).
        self.network.save_weights(self.weights)

    def detect(self, instance):
        # Event detection.
        return list(self.network.predict(instance)[0])


# Run ML.
def run_ML(input_file, output_file, weights, prn, date, plot=False, threshold=0, location=''):
    # Read data.
    DF = pd.read_csv(input_file)

    # Define signal types.
    signal_type_names = {"G": {"1": "L1CA", "4": "L2Y", "5": "L2C", "6": "L2P", "7": "L5Q"},
                         "R": {"1": "L1CA", "3": "L2CA", "4": "L2P"},
                         "E": {"1": "E1", "2": "E5A", "3": "E5B", "4": "AltBOC"}}

    # Process one signal type at a time.
    signal_types = set(list(DF['SigType']))
    for signal_type in signal_types:

        # Obtain signal type name.
        signal_type_name = signal_type_names[prn[0]][str(signal_type)]

        # Filter data set for that signal type.
        DF1 = DF[DF['SigType'] == signal_type]

        # Process one period at a time.
        start_times, end_times = time_ranges(input_file, threshold=threshold, elev_col_name='Elevation',
                                             times_col_name='GPS TOW')
        for e, (start_time, end_time) in enumerate(zip(start_times, end_times), 1):
            # Filter data frame.
            X = DF1[DF1['GPS TOW'] >= start_time]
            X = X[X['GPS TOW'] < end_time]

            # Extract columns.
            GPS_TOW = X['GPS TOW']
            X = X[['Elevation', 'CNo', 'S4', 'S4 Cor']]

            # Normalize.
            X['Elevation'] = X['Elevation'].div(90)
            X['CNo'] = X['CNo'].div(60)

            # Create RNN model.
            ML_model = RNNModel(weights, load_weights=True)

            # Detect scintillation.
            y = []
            for row in np.asarray(X).astype('float32'):
                instance = np.expand_dims(row, axis=0)
                output = ML_model.detect(instance)
                y.append(output.index(max(output)))

            # Add GPS TOW and y to the data frame.
            X['GPS TOW'] = GPS_TOW
            X['y'] = y

            # De-normalize the values.
            X['Elevation'] = X['Elevation'].div(1/90)
            X['CNo'] = X['CNo'].div(1/60)

            # Create the output directory if it doesn't exist.
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Save scintillation events to a new file.
            new_file = output_file[:-4] + '_{}_{}.csv'.format(signal_type_name, e)
            X.to_csv(new_file, index=False)

            # Plot.
            if plot:
                # Plot.
                plt = plot_scintillation_detections(new_file, 'S4', prn, threshold, location, signal_type_name, date,
                                                    time_period=e)

                # Show plot.
                plt.show()
