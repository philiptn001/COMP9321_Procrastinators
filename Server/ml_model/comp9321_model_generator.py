from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import pandas as pd
import pickle
file = '../data_preprocessing/preprocessed.csv'
df = pd.read_csv(file)
print(df.head())

y = df["price"]
df = df.drop("price", axis=1)
df = df.drop("name", axis=1)
df = df.drop("Average Repair Cost", axis=1)
df = df.drop("Reliability Index", axis=1)
powerPS = df["powerPS"]
df = df.drop("powerPS", axis=1)
kilometer = df["kilometer"]
df = df.drop("kilometer", axis=1)
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(df)
x = enc.transform(df)
X = []
for vals in x:
  X.append(vals.toarray()[0].tolist())

for i in range(len(X)):

  X[i] = X[i] + [powerPS[i]] + [kilometer[i]]

regressor = DecisionTreeRegressor(random_state=0)

y = y.values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

regressor.fit(X_train,y_train)

y_pred = regressor.predict(X_test)

# print(y_predict)
score = r2_score(y_test, y_pred)

print(score)

print(y_test[:5])

print(y_pred[:5])

f = open('model', 'wb')
f.write(pickle.dumps(regressor))
f.close()

f = open('encoder', 'wb')
f.write(pickle.dumps(enc))
f.close()
