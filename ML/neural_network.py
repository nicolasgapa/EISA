"""
2020
Embry-Riddle Aeronautical University
Department of Physics and Life Sciences

Code developer: Nicolas Gachancipa

Embry-Riddle Ionospheric Algorithm (EISA) 2.0
Machine Learning (ML) for atmospheric data analysis
Neural Networks (NNs)

"""
# Imports
from Graphing.support_graphing_functions import time_ranges
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
from ML.support_ML_functions import plot_scintillation_detections
import numpy as np
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Import TensorFlow ('TF_CPP_MIN_LOG_LEVEL' = '3' means no warnings/errors will be printed in the command window.)
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import tensorflow.keras as k

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

filesep = os.sep  # File separator (Changes between windows, linux and other OS).


# Class.
class NNModel:
    """
    Neural Network model.
    """

    def __init__(self, scintillation_type):
        """
        :param scintillation_type: 'S4' or 'sigma'
        """

        # Define input length and number of output categories.
        """
        input_length (int): Length of the input to the neural network. For example, for a data instance containing
                            4 parameters (eg. ['Elevation', 'S4', 'S4 Cor', 'CNo']), the input_length = 4.
        output_categories (int): The number of output categories. E.g. 2 for binary, or 4 for multi-class classification
                                 with 4 different labels.
        """
        self.scintillation_type = scintillation_type
        if self.scintillation_type == 'S4':
            # S4 scintillation has 4 inputs ('Elevation', 'S4', 'S4 Cor', 'CNo'), and 5 outputs indicating the type
            # of scintillation: {0: 'No Scintillation', 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Multi-Path'}
            input_length, output_categories = 4, 5
        elif self.scintillation_type == 'sigma':
            # Sigma scintillation has 5 inputs ('Elevation', '1SecSigma', '30SecSigma', '60SecSigma', 'CMC Std'), and
            # 6 outputs indicating the type of scintillation: {0: 'No Scintillation', 1: 'Low', 2: 'Medium', 3: 'High',
            # 4: 'Extreme', 5: 'Multi-Path'}
            input_length, output_categories = 7, 6
        else:
            raise Exception("scintillation type must be 'S4' or 'sigma'.")

        # Neural network.
        self.network = k.models.Sequential([k.layers.Dense(units=120, activation='relu',
                                                           input_shape=(None, input_length)),
                                            k.layers.Dense(60, activation="relu"),
                                            k.layers.Dense(40, activation="relu"),
                                            k.layers.Dense(20, activation="relu"),
                                            k.layers.Dense(10, activation="relu"),
                                            k.layers.Dense(units=output_categories, activation='softmax')])

    def train(self, training_file, output_weights, load_weights=False, input_weights='',
              optimizer='adam', loss='categorical_crossentropy', epochs=100,
              batch_size=100):
        # Print status.
        print('Training using: {}.'.format(training_file))

        # Get training data.
        df = pd.read_csv(training_file)

        # Normalization.
        df['Elevation'] = df['Elevation'].div(90)
        if self.scintillation_type == 'S4':
            df['CNo'] = df['CNo'] - 20
            df['CNo'] = df['CNo'].div(40)

        # Formatting.
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
        checkpoint = ModelCheckpoint(output_weights, verbose=1, monitor='loss',
                                     save_best_only=True, mode='auto')

        # Compile and fit.
        if load_weights:
            self.network.load_weights(input_weights)
        self.network.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
        self.network.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=[checkpoint])

        # Load best weights into network.
        self.load_weights(output_weights)

    def detect(self, instance):
        # Event detection.
        return list(self.network.predict(instance)[0])

    def load_weights(self, weights):
        # Load weights.
        self.network.load_weights(weights)


# Run ML.
def run_ML(input_file, output_file, neural_network_model, prn, date, scintillation_type='S4', threshold=0, location='',
           show_plot=False, save_plot=False, save_plot_dir=''):
    """
    Run the machine learning module.

    :param input_file: (str) Input csv file containing the data. For S4 scintillation, the file must contain the
                             following columns: ['Elevation', 'CNo', 'S4', 'S4 Cor']. For sigma scintillation, the file
                             must contain the following columns: ['Elevation', '1SecSigma', '3SecSigma', '10SecSigma',
                             '30SecSigma', '60SecSigma', 'CMC Avg']. The files may contain more columns, which will be
                             discarded.
    :param output_file: (str) The name of the output file (including the directory if applicable).
    :param neural_network_model: (NNModel) Neural Network model with H5 weights loaded.
    :param prn: (str) The satellite number. E.g. 'G1' for GPS 1 or 'R5' for GLONASS 5.
    :param date: (str) Date in the format [year, month, day]. E.g. [2021, 2, 5] for February 5th, 2021.
    :param scintillation_type (str): Either 'S4' (for amplitude) or 'sigma' (for phase) scintillation.
    :param plot (bool): True if you want to display the plot after running the ML module.
    :param save_plot (bool): Saves the plot (if True) in the specified save_plot_dir.
    :param save_plot_dir (str): Directory to save the plot (Only works if save_plot == True).
    :param threshold (float): The elevation threshold.
    :param location (str): The location of the receiver. E.g. 'Daytona Beach, FL'

    :return: Creates the output csv file and plots, identifying scintillation events. The function returns a list of
             all the scintillaiton files that were created.
    """
    # Validation.
    if scintillation_type not in ['S4', 'sigma']:
        raise Exception("The scintillation_type must be either 'S4' or 'Sigma'.")

    # Read data.
    DF = pd.read_csv(input_file)

    # Define signal types and time periods dictionary.
    signal_type_names = {"G": {"1": "L1CA", "4": "L2Y", "5": "L2C", "6": "L2P", "7": "L5Q"},
                         "R": {"1": "L1CA", "3": "L2CA", "4": "L2P"},
                         "E": {"1": "E1", "2": "E5A", "3": "E5B", "4": "AltBOC"}}
    time_period_vars = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J'}

    # Create a empty folder that will hold the names of the csv files that are created.
    output_files = []

    # Process one signal type at a time.
    signal_types = set(list(DF['SigType']))
    for signal_type in signal_types:

        # Obtain signal type name.
        signal_type_name = signal_type_names[prn[0]][str(signal_type)]

        # Filter data set for that signal type. Save the filtered dataset into a new variable (DF1), since the original
        # DF will be used in the following run of the loop.
        DF1 = DF[DF['SigType'] == signal_type]

        # Process one period at a time.
        """
        When a satellite passes over the receiver more than once during the same day, each range of times at which 
        the satellite locked to the receiver is a time period. For example, let us say that satellite G1 passes over 
        the receiver twice in a day; First, between 6AM and 8AM, and then between 8PM and 10PM. The period between 
        6AM and 8AM is therefore time_period == 1, while the 8PM-10PM corresponds to time_period == 2.
        """
        start_times, end_times = time_ranges(input_file, threshold=threshold, elev_col_name='Elevation',
                                             times_col_name='GPS TOW')
        for time_period, (start_time, end_time) in enumerate(zip(start_times, end_times), 1):
            # Filter data frame. Save filtered df into a new variable (X).
            X = DF1[DF1['GPS TOW'] >= start_time]
            X = X[X['GPS TOW'] < end_time]

            # Filter 60 sec sigma errors (values above the normal range are usually related to receiver/computer
            # errors or multipath). The values must be removed, otherwise, the plots will be useless (since some
            # erroneous values sometimes are above 1e6).
            if scintillation_type == 'sigma':
                X = X[X['60SecSigma'] <= 5]

            # Extract columns (corresponding to the scintillation type).
            GPS_TOW = X['GPS TOW']
            if scintillation_type == 'S4':
                X = X[['Elevation', 'CNo', 'S4', 'S4 Cor']]
            elif scintillation_type == 'sigma':
                X = X[['Elevation', '1SecSigma', '3SecSigma', '10SecSigma', '30SecSigma', '60SecSigma', 'CMC Std']]

            # Normalize elevation.
            X['Elevation'] = X['Elevation'].div(90)

            # Normalize carrier to noise ratio (for s4 scintillation only).
            if scintillation_type == 'S4':
                X['CNo'] = X['CNo'] - 20
                X['CNo'] = X['CNo'].div(40)

            # Detect scintillation (Continue if the data frame is empty or only contains a few data instances <= 10).
            if len(X) > 10:
                input_array = np.expand_dims(np.asarray(X).astype('float32'), axis=0)
                output = neural_network_model.detect(input_array)
                y = [list(o).index(max(list(o))) for o in output]
            else:
                continue

            # Create a output data frame and add GPS TOW and scintillation labels (y) to it.
            DF_out = X.copy()
            DF_out['GPS TOW'] = GPS_TOW
            DF_out['y'] = y

            # De-normalize the values.
            DF_out['Elevation'] = DF_out['Elevation'].div(1 / 90)
            if scintillation_type == 'S4':
                DF_out['CNo'] = DF_out['CNo'].div(1 / 60)

            # Create the output directory if it doesn't exist.
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Save scintillation events data frame to a new csv file (Only if scintillation or multi-path events
            # have been identified).
            if any(x > 0 for x in map(int, list(set(y)))):

                # Create CSV file. Add the scintillation type, signal type, and time period to the name.
                new_file = output_file + '_{}_{}_{}.csv'.format(scintillation_type, signal_type_name,
                                                                time_period_vars[time_period])
                print('Creating file: {}.  PRN: {}.'.format(new_file, prn))
                DF_out.to_csv(new_file, index=False)
                output_files.append(new_file)

                # Plot.
                if show_plot or save_plot:
                    # Plot.
                    graph_type = '60SecSigma' if scintillation_type == 'sigma' else 'S4'
                    sci_plt, graph_name = plot_scintillation_detections(new_file, graph_type, prn, threshold, location,
                                                                        signal_type_name, date, time_period=time_period)

                    # Show plot.
                    if show_plot:
                        sci_plt.show()

                    # Save the plot.
                    if save_plot:
                        # Create the output directory if it does not exist.
                        if not os.path.exists(save_plot_dir):
                            os.makedirs(save_plot_dir)

                        # Save the figure.
                        print('Saving plot: {}.png'.format(save_plot_dir + filesep + graph_name + '.png'))
                        sci_plt.savefig(save_plot_dir + filesep + graph_name + '.png')

                    # Reset matplotlib plt.
                    sci_plt.clf()

    # Return the names of the created files.
    return output_files
