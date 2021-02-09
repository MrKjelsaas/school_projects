import sys
sys.path.insert(0, 'C:\coding_projects\machine_learning_practice')
import MLfunctions as ML
import numpy as np

training_data_fraction = 0.8
learning_rate = 0.01
number_of_epochs = 50000

# Import data
data = np.loadtxt("../data/winequality-red.csv", delimiter=";", skiprows=1)
np.random.shuffle(data)
m = np.shape(data)[0]
n = np.shape(data)[1] - 1

data, scaler = ML.feature_scale(data)

training_data = data[:int(training_data_fraction*m), :]
test_data = data[int(training_data_fraction*m):, :]

W = ML.random_weights(n+1)

X = training_data[:, :n]
X = np.c_[np.ones(len(training_data)), X]
y = training_data[:, -1]


# Train the model
print("Training model...\n")
for epoch in range(number_of_epochs):
    W -= learning_rate*ML.linReg.gradient(W, X, y, lambdaRegulator = 0.1)

X = test_data[:, :n]
X = np.c_[np.ones(len(test_data)), X]
y = test_data[:, -1]

# First five results
predictions = ML.linReg.hypothesis(W, X.T)
predictions = np.round(predictions)
print("Prediction:")
print(predictions[:10])
print("\nActual:")
print(y[:10])

correct = 0
for n in range(len(y)):
    if predictions[n] == y[n]:
        correct += 1
accuracy = correct / len(y)

print("\nAccuracy:")
print(accuracy)
print("")
