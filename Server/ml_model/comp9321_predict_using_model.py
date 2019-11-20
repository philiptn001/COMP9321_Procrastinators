import pandas as pd
import pickle

df = ["coupe", "2000", "manually", "911", "Apr", "petrol", "Porsche", "No"]

powerPS = [300]
kilometer = [150000]

f = open('encoder', 'rb')
enc = pickle.loads(f.read())

x = enc.transform([df])
X = []
X.append(x.toarray()[0].tolist())
X = X[0] + powerPS + kilometer
f = open('model', 'rb')
regressor = pickle.loads(f.read())

y_pred = regressor.predict([X])

print(str(y_pred))