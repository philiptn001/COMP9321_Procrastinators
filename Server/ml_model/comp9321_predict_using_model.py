import pandas as pd
import pickle

# df = ["limousine", "automatic", "golf", "petrol", "Volkswagen", "No"]

# df = ["limousine", "automatic", "a6", "diesel", "Audi", "No"]

df = ["limousine", "automatic", "5er", "diesel", "BMW", "No"]

powerPS = [300]
kilometer = [15000]
yearOfRegistration = [2014]

f = open('encoder', 'rb')
enc = pickle.loads(f.read())

x = enc.transform([df])
X = []
X.append(x.toarray()[0].tolist())
X = X[0] + yearOfRegistration + powerPS + kilometer
f = open('model', 'rb')
regressor = pickle.loads(f.read())

y_pred = regressor.predict([X])

print(str(y_pred))