import pandas as pd
import numpy as np

if __name__ == '__main__':
    file = 'Server/data_preprocessing/autos.csv'
    df = pd.read_csv(file, encoding="latin-1")

    #dropping the columns that we don't need
    cols= [0, 2, 3, 5, 16, 17, 18, 19]
    df = df.drop(df.columns[cols], axis=1)

    #changing NaN values to 'other' or 'unknown' based on context
    df["vehicleType"].fillna("other", inplace=True)
    df["model"].fillna("other", inplace=True)
    df["fuelType"].fillna("other", inplace=True)
    df["gearbox"].fillna("unknown", inplace=True)
    df["notRepairedDamage"].fillna("unknown", inplace=True)

    df = df[pd.notnull(df['price'])]
    df = df[df.vehicleType != 'volkswagen']

    #Removing invalid vehicle registration years
    df = df[(df["yearOfRegistration"] >= 1950) & (df["yearOfRegistration"] <= 2019)]
    df = df[(df["price"] >= 100.0)]
    df = df[(df["powerPS"] >= 50.0)]

    df["monthOfRegistration"].replace([0, 12], [1, 11], inplace=True)


    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    df["monthOfRegistration"].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], months, inplace=True)

    median = df.groupby("vehicleType")["price"].median()

    # 75th percentile of the prices of all the vehicles types
    quantile75 = df.groupby("vehicleType")["price"].quantile(0.75)

    # 25th percentile of the prices of all the vehicles types
    quantile25 = df.groupby("vehicleType")["price"].quantile(0.25)

    # Calculating the value of the prices of each vehicle type above which all the values are outliers
    iqr = (quantile75 - quantile25) * 1.5 + median



    # Removing the outliers as per the logic above
    df = df[((df["vehicleType"] == "small car") & (df["price"] <= iqr['small car'])) |
            ((df["vehicleType"] == "other") & (df["price"] <= iqr['other'])) |
            ((df["vehicleType"] == "suv") & (df["price"] <= iqr['suv'])) |
            ((df["vehicleType"] == "station wagon") & (df["price"] <= iqr['station wagon'])) |
            ((df["vehicleType"] == "bus") & (df["price"] <= iqr['bus'])) |
            ((df["vehicleType"] == "cabrio") & (df["price"] <= iqr['cabrio'])) |
            ((df["vehicleType"] == "limousine") & (df["price"] <= iqr['limousine'])) |
            ((df["vehicleType"] == "coupe") & (df["price"] <= iqr['coupe'])) ]


    #fixing columns with mixed types
    df["kilometer"] = pd.to_numeric(df["kilometer"])


    # Reading the second csv
    df_rel = pd.read_csv('Server/data_preprocessing/car_reliability.csv')

    df_rel = df_rel.drop(df_rel.columns[3:], axis=1)
    df_rel = df_rel.drop(df_rel.columns[0], axis=1)

    # Reading the third csv

    df_avgcost = pd.read_csv('Server/data_preprocessing/avgrepaircost.csv')
    df_avgcost = df_avgcost.drop(df_avgcost.columns[0], axis=1)


    join_df = pd.merge(df_avgcost, df_rel, how='left', left_on=['Make and Model'], right_on=['Make and Model'])


    df['brand'] = df['brand'].str.capitalize()

    df['brand'] = df['brand'].apply(lambda x: 'Mercedes-Benz' if 'Mercedes_benz' in x else x.replace('_', ' '))
    df['brand'] = df['brand'].apply(lambda x: x.upper() if 'Bmw' in x else x)
    df['brand'] = df['brand'].apply(lambda x: x.upper().replace(' ','') if 'Land rover' in x else x)

    main_df = pd.merge(df, join_df, how='left', left_on=['brand'], right_on=['Make and Model'])
    main_df = main_df.drop('Make and Model', axis=1)

    main_df = main_df.dropna()


   # print(main_df.head(5).to_string())
    main_df.to_csv("preprocessed.csv", index=False)



