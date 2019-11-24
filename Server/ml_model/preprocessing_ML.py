import pandas as pd

df = pd.read_csv('../data_preprocessing/preprocessed.csv')

df = df.drop("Average Repair Cost", axis=1)
df = df.drop("Reliability Index", axis=1)
df = df[(df["vehicleType"] != "other")]
df = df[(df["notRepairedDamage"] != "unknown")]
df = df[(df["model"] != "andere")]
df = df[(df["fuelType"] != "other")]
# df = df[(df["model"] == "golf")].sort_values(by=['yearOfRegistration'])
# df = df.sort_values(by=['yearOfRegistration'])

# df = df.drop("vehicleType", axis=1)
# df = df.drop("gearbox", axis=1)
# df = df.drop("powerPS", axis=1)
# df = df.drop("kilometer", axis=1)
# df = df.drop("monthOfRegistration", axis=1)
# df = df.drop("notRepairedDamage", axis=1)
# df = df.drop("fuelType", axis=1)
# count = df['model'].value_counts()
# print(count[count>5000])

# df = df[df.model.isin([key for key in count.index if count[key] > 5000])]

print(len(df))

df.to_csv("preprocessed_ml.csv", index=False)
