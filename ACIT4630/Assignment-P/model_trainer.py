

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM#, CuDNNLSTM

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)



import numpy as np
import time



make_labels_categorical = False
train_test_split = 0.8





# Import data
data = np.loadtxt("Data/main_data_file.txt")
np.random.shuffle(data)
m = np.shape(data)[0] # Number of samples
n = np.shape(data)[1] - 1 # Number of features

# Feature scale
for i in range(n-1):
    mean = np.mean(data[:, i])
    std = np.std(data[:, i])
    data[:, i] -= mean
    if std != 0:
        data[:, i] /= std
data[:, -1] *= 100

if make_labels_categorical is True:
    for n in range(m):
        if data[n, -1] < -0.5:
            data[n, -1] = 0
        elif -0.5 < data[n, -1] < 0.5:
            data[n, -1] = 1
        else:
            data[n, -1] = 2

x_train = data[:int(np.shape(data)[0] * train_test_split), :-1]
x_test = data[int(np.shape(data)[0] * train_test_split):, :-1]
y_train = data[:int(np.shape(data)[0] * train_test_split), -1]
y_test = data[int(np.shape(data)[0] * train_test_split):, -1]


print(np.shape(x_train))
print(np.shape(x_test))
print(np.shape(y_train))
print(np.shape(y_test))




model = Sequential()

model.add(Dense(n, activation='relu'))
#model.add(Dropout(0.2))

model.add(Dense(2*n, activation='relu'))
#model.add(Dropout(0.2))

model.add(Dense(2*n, activation='relu'))
#model.add(Dropout(0.2))

model.add(Dense(n, activation='relu'))
#model.add(Dropout(0.2))

model.add(Dense(1))



opt = tf.keras.optimizers.Adam(lr=0.001, decay=1e-6)

# Compile model
model.compile(
    loss='MeanSquaredError',
    optimizer=opt,
    metrics=['accuracy'],
)

model.fit(x_train,
          y_train,
          epochs=100,
          validation_data=(x_test, y_test))
