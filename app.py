from flask import Flask
from flask import send_from_directory
from flask_cors import CORS
from flask import request
import json
from flask import jsonify
import os

import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/",  methods = ['POST'])
def hello():
    data_dir = os.getcwd()+'/data/'
    params = request.json
    print('Params:', params)
    apisFile = params['apisFile']
    formCFile = params['formCFile']
    dfree=pd.read_excel(formCFile)
    #df.columns = ['Date','Passport','Customer','Item','Qty','Flight']
    #dfree['System Date'] = pd.to_datetime(dfree['System Date'])
    #dfree['System Date'] = dfree['System Date'].dt.date
    dfree['Passport No.'] = dfree['Passport No.'].astype(str)
    dfree['Passport No.'] = dfree['Passport No.'].str.strip()
    dfree.drop_duplicates()
    #df.set_index(['System Date','Passport No.'],inplace=True)
    #df.sort_index(level=['System Date','Passport No.'],inplace=True)
    #df.loc[(slice(None),'L7454560'),:]
    #df.to_excel('20.xlsx')
    print("2.Finished Reading Duty Free Data ...............................")
    print(dfree.info())
    print("3.Now reading Flights Data. This might take a while ...............................")
    #files = ['JanExcels/flights/6E0251to10Jan.xlsx','JanExcels/flights/6E02511to20Jan.xlsx','JanExcels/flights/6E02521to31Jan.xlsx']
    #files = glob.glob("./JanExcels/flights/apis.xlsx")
    #files = glob.glob("./test/set1/*.xlsx")
    df2=pd.read_excel(apisFile,usecols=[1,2,3,4,5,6,7,8,9,10,11,12])
    df2['Schedule Date'] = pd.to_datetime(df2['Schedule Date'])
    df2['Schedule Date'] = df2['Schedule Date'].dt.date
    df2['Date of Birth'] = pd.to_datetime(df2['Date of Birth'])
    df2['Date of Birth'] = df2['Date of Birth'].dt.date
    df2['Passport No.'] = df2['Passport No.'].astype(str)
    df2['Passport No.'] = df2['Passport No.'].str.strip()
    df2['Flight No.'] = df2['Flight No.'].astype(str)
    df2.fillna("Not Available",inplace=True)
    df2.drop_duplicates()
    print("4.Finished reading Flights Data ...............................")
    print(df2.info())
    print("5.Merging data ...............................")
    merged=pd.merge(dfree, df2, left_on='Passport No.', right_on='Passport No.', how="left")
    merged.drop_duplicates()
    print(merged.info())
    #returnVal = merged.to_json(orient='records')
    #merged.to_excel('merged.xlsx')
    print("6.Storing matched data in matched.xlsx ...............................")
    matched = merged.loc[merged['Name'].notnull()];
    matched.drop_duplicates()
    #matched.to_excel(data_dir+'matched.xlsx')
    print("7.matched.xlsx is ready ...............................")
    print("8.Storing unmatched data in unmatched.xlsx ...............................")
    unmatched = merged.loc[merged['Name'].isnull()];
    unmatched.drop_duplicates();
    #unmatched.to_excel(data_dir+'unmatched.xlsx')
    print("9.unmatched.xlsx is ready ...............................")
    return jsonify({'matched': matched.head(1000).to_json(orient='records'), 'unmatched': unmatched.head(1000).to_json(orient='records')})

@app.route('/data/<path:filepath>')
def data(filepath):
    return send_from_directory('data', filepath)

if __name__ == "__main__":
	app.run()