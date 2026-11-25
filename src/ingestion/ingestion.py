import pandas as pd


try:
    df=pd.read_csv(r"C:/Users/Dell/OneDrive/Documents/Project_03_Kerala_Monsoon_Detailed_Specification/data/raw/Kerala-Rainfall-Historical.csv")
    print('Dataset Loaded')
    print()
except FileNotFoundError:
    print('File not Found')
    print()
    raise

print('first 5 Records')
print(df.head())
print()

print('Dataset Information')
print(df.info())
print()


print('Missing Values')
print(df.isnull().sum())
print()

print("Total Records : ",len(df))
print()
print(f'Shape : {df.shape}  \nSize:{df.size}')



months=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

df['YEAR']=pd.to_numeric(df["YEAR"],errors='coerce')

for month in months:
    df[month]=pd.to_numeric(df[month],errors='coerce')


valid = df['YEAR'].between(1901,2017)

for month in months:
    valid = valid & (df[month]>=0) & df[month].notna()

cleandf=df[valid].copy()
invaliddf=df[~valid].copy()
print()
print('Total Records : ',len(df))
print('Valid Records : ',len(cleandf))
print('Invalid Record : ',len(invaliddf))


cleandf["YEAR"]=cleandf['YEAR'].astype(int)
cleandf.to_csv("data/processed/clean_kerala_monsoon.csv",index=False)
print()
print('Clean Dataset Saves Successfully ')

with open("data/processed/monsoon_ingestion_audit.log", "w") as file:
    file.write('Kerala Monsoon Data Ingestion Audit \n')
    file.write('------------------------------------\n')
    file.write(f'Total Record : {len(df)}\n')
    file.write(f'Valid Records : {len(cleandf)}\n')
    file.write(f'Rejected Records : {len(invaliddf)}\n')
    file.write(
        f'Year Coverge : {cleandf["YEAR"].min()} - '
        f'{cleandf['YEAR'].max()}\n'    
        )
    file.write('\nREjected Records :\n')

    for index , row in invaliddf.iterrows():
        file.write(f'Row {index +2 } : {row.to_dict()}\n')
    print('Audit Log Generated Successfully')