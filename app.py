from flask import Flask
from flask import send_from_directory
from flask_cors import CORS
from flask import request
import json
from flask import jsonify
import os
import datetime
import fuzzymatcher
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/",  methods = ['GET'])
def sayHello()
    return "Hola!"

@app.route("/",  methods = ['POST'])
def notFuzzy():
    print("Non-Fuzzy Called!")
    data_dir = os.getcwd()+'/data/'
    now=datetime.datetime.now()
    matchedFileName='matched'+str(now)+'.xlsx';
    unmatchedFileName='unmatched'+str(now)+'.xlsx';
    mergedFileName='merged'+str(now)+'.xlsx';
    params = request.json
    print('Params:', params)
    apisFile = params['apisFile']
    formCFile = params['formCFile']
    dfree=pd.read_excel(formCFile)
    if 'passport_number' in dfree.columns:
        dfree['passport_number'] = dfree['passport_number'].astype(str)
        dfree['passport_number'] = dfree['passport_number'].str.strip()
    else:
        return jsonify({
            'error': True,
            'errorMessage': "Error processing: passport_number column not found in the uploaded Form C Excel file"
        })
    dfree.drop_duplicates()
    print("2.Finished Reading Duty Free Data ...............................")
    print(dfree.info())
    print("3.Now reading Flights Data. This might take a while ...............................")
    arrivals=pd.read_excel(apisFile)
    if 'passenger_name' not in arrivals.columns:
        return jsonify({
                            'error': True,
                            'errorMessage': "Error processing: passenger_name column not found in the uploaded Apis Excel file"
                        })
    if 'scheduled_date' in arrivals.columns:
        arrivals['scheduled_date'] = pd.to_datetime(arrivals['scheduled_date'])
        arrivals['scheduled_date'] = arrivals['scheduled_date'].dt.date
    if 'dob' in arrivals.columns:
        arrivals['dob'] = pd.to_datetime(arrivals['dob'])
        arrivals['dob'] = arrivals['dob'].dt.date
    if 'passport_number' in arrivals.columns:
        arrivals['passport_number'] = arrivals['passport_number'].astype(str)
        arrivals['passport_number'] = arrivals['passport_number'].str.strip()
    else:
        return jsonify({
                    'error': True,
                    'errorMessage': "Error processing: passport_number column not found in the uploaded Apis Excel file"
                })
    if 'flight_number' in arrivals.columns:
        arrivals['flight_number'] = arrivals['flight_number'].astype(str)
    arrivals.fillna("Not Available",inplace=True)
    arrivals.drop_duplicates()
    print("4.Finished reading Flights Data ...............................")
    print(arrivals.info())
    print("5.Merging data ...............................")
    merged=pd.merge(dfree, arrivals, left_on='passport_number', right_on='passport_number', how="left")
    merged.drop_duplicates()
    #merged.to_excel(data_dir+mergedFileName)
    print(merged.info())
    print("6.Storing matched data in matched.xlsx ...............................")
    matched = merged.loc[merged['passenger_name'].notnull()];
    matched.drop_duplicates()
    matched.to_excel(data_dir+matchedFileName)
    print("7.matched.xlsx is ready ...............................")
    print("8.Storing unmatched data in unmatched.xlsx ...............................")
    unmatched = merged.loc[merged['passenger_name'].isnull()];
    unmatched.drop_duplicates();
    unmatched.to_excel(data_dir+unmatchedFileName)
    print("9.unmatched.xlsx is ready ...............................")
    return jsonify({'matched': matched.head(1000).to_json(orient='records'),
                    'unmatched': unmatched.head(1000).to_json(orient='records'),
                    'matchedFileName': matchedFileName,
                    'unmatchedFileName': unmatchedFileName,
                    'error': False
                    })

@app.route('/fuzzy',methods = ['POST'])
def fuzzy():
    print("Fuzzy Called!")
    data_dir = os.getcwd()+'/data/'
    now=datetime.datetime.now()
    matchedFileName='matched'+str(now)+'.xlsx';
    params = request.json
    print('Params:', params)
    apisFile = params['apisFile']
    formCFile = params['formCFile']
    otherCompareList = params['otherCompareList']
    left_on=list(otherCompareList)
    right_on=list(otherCompareList)
    cust_index=-1
    try:
        cust_index = right_on.index("customer_name")
    except:
        cust_index=-1
    if cust_index!=-1:
        right_on[cust_index]="passenger_name"
    print("left_on:", left_on)
    print("right_on:", right_on)
    print("1.Reading Duty Free Data ...............................")
    dfree=pd.read_excel(formCFile)
    if 'passport_number' in dfree.columns:
        dfree['passport_number'] = dfree['passport_number'].astype(str)
        dfree['passport_number'] = dfree['passport_number'].str.strip()
    else:
        return jsonify({
                'error': True,
                'errorMessage': "Error processing: passport_number column not found in the uploaded Form C Excel file"
        })
    if 'customer_name' in dfree.columns:
        dfree['customer_name'] = dfree['customer_name'].astype(str)
        dfree['customer_name'] = dfree['customer_name'].str.strip()
    else:
        return jsonify({
                    'error': True,
                    'errorMessage': "Error processing: customer_name column not found in the uploaded Form C Excel file"
        })
    if 'flight_number' in dfree.columns:
        dfree['flight_number'] = dfree['flight_number'].astype(str)
        dfree['flight_number'] = dfree['flight_number'].str.strip()
    else:
        return jsonify({
                    'error': True,
                    'errorMessage': "Error processing: flight_number column not found in the uploaded Form C Excel file"
    })
    dfree.drop_duplicates()
    print("2.Finished Reading Duty Free Data ...............................")
    print(dfree.info())
    print("3.Now reading Flights Data. This might take a while ...............................")
    arrivals=pd.read_excel(apisFile)
    if 'passport_number' in arrivals.columns:
        arrivals['passport_number'] = arrivals['passport_number'].astype(str)
        arrivals['passport_number'] = arrivals['passport_number'].str.strip()
    else:
        return jsonify({
                'error': True,
                'errorMessage': "Error processing: passport_number column not found in the uploaded APIS Excel file"
        })
    if 'passenger_name' in arrivals.columns:
        arrivals['passenger_name'] = arrivals['passenger_name'].astype(str)
        arrivals['passenger_name'] = arrivals['passenger_name'].str.strip()
    else:
        return jsonify({
                    'error': True,
                    'errorMessage': "Error processing: passenger_name column not found in the uploaded APIS Excel file"
        })
    if 'flight_number' in arrivals.columns:
        arrivals['flight_number'] = arrivals['flight_number'].astype(str)
        arrivals['flight_number'] = arrivals['flight_number'].str.strip()
    else:
        return jsonify({
                    'error': True,
                    'errorMessage': "Error processing: flight_number column not found in the uploaded APIS Excel file"
    })
    arrivals.fillna("Not Available",inplace=True)
    arrivals.drop_duplicates()

    print("4.Finished reading Flights Data ...............................")
    print(arrivals.info())
    print("5. Applying match algorithm....")
    matched = fuzzymatcher.fuzzy_left_join(dfree, arrivals, left_on, right_on)
    matched.to_excel(data_dir+matchedFileName)
    print("6.matched.xlsx is ready ...............................")
    return jsonify({'fuzzyMatched': matched.head(1000).to_json(orient='records'),
                        'fuzzyMatchedFileName': matchedFileName,
                        'error': False
                        })

@app.route('/data/<path:filepath>')
def data(filepath):
    return send_from_directory('data', filepath)

if __name__ == "__main__":
	app.run(host='0.0.0.0')