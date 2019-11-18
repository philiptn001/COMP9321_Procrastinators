from googletrans import Translator
import pandas as pd

f = open('autos.csv', 'r')
data = []
translator = Translator()
for vals in f.readlines():
    vals = vals.replace('\n', '')
    temp = vals.split(',')
    for i in range(len(temp)):
        a = translator.translate(temp[i], dest='en')
        temp[i] = a.text
    data.append(temp)
df = pd.DataFrame(data = data[1:], columns= data[0])
df.to_csv("translatedCSV.csv", index=False)