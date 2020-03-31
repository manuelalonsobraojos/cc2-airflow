from flask import Flask, jsonify
from statsmodels.tsa.arima_model import ARIMA
import pandas as pd
import pmdarima as pm
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)
mongo_client=MongoClient('mongodb://127.0.0.1:27017/')

@app.route('/servicio/v1/prediccion/24horas/')
def prediction24():
	hour = 24
	db=mongo_client.cc
	collection = db.prediction
	data = collection.find_one({'index':'SF'})
	data_humidity = algorithmH(data, hour)
	data_temperature = algorithmT(data, hour)
	data_dict = doDict(data_humidity, data_temperature, hour)

	return jsonify(data_dict)

@app.route('/servicio/v1/prediccion/48horas/')
def prediction48():
	hour = 48
	db=mongo_client.cc
	collection = db.prediction
	data = collection.find_one({'index':'SF'})
	data_humidity = algorithmH(data, hour)
	data_temperature = algorithmT(data, hour)
	data_dict = doDict(data_humidity, data_temperature, hour)

	return jsonify(data_dict)

@app.route('/servicio/v1/prediccion/72horas/')
def prediction72():
	hour = 72
	db=mongo_client.cc
	collection = db.prediction
	data = collection.find_one({'index':'SF'})
	data_humidity = algorithmH(data, hour)
	data_temperature = algorithmT(data, hour)
	data_dict = doDict(data_humidity, data_temperature, hour)

	return jsonify(data_dict)

def algorithmH(collection, hours):
	df = pd.DataFrame(collection["datos"])

	model = pm.auto_arima(df["humidity"].fillna(0) , start_p=1, start_q=1,
		                  test='adf',  # use adftest to find optimal 'd'
		                  max_p=3, max_q=3,  # maximum p and q
		                  m=1,  # frequency of series
		                  d=None,  # let model determine 'd'
		                  seasonal=False,  # No Seasonality
		                  start_P=0,
		                  D=0,
		                  trace=True,
		                  error_action='ignore',
		                  suppress_warnings=True,
		                  stepwise=True)

    # Forecast
	n_periods = hours  # One day
	fc, confint = model.predict(n_periods=n_periods, return_conf_int=True)

	# fc contains the forecasting for the next 24 hours.
	print(fc)
	return fc

def algorithmT(collection, hours):
	df = pd.DataFrame(collection["datos"])

	model = pm.auto_arima(df["temperature"].fillna(0) , start_p=1, start_q=1,
		                  test='adf',  # use adftest to find optimal 'd'
		                  max_p=3, max_q=3,  # maximum p and q
		                  m=1,  # frequency of series
		                  d=None,  # let model determine 'd'
		                  seasonal=False,  # No Seasonality
		                  start_P=0,
		                  D=0,
		                  trace=True,
		                  error_action='ignore',
		                  suppress_warnings=True,
		                  stepwise=True)

	# Forecast
	n_periods = hours  # One day
	fc, confint = model.predict(n_periods=n_periods, return_conf_int=True)

	# fc contains the forecasting for the next 24 hours.
	print(fc)
	return fc

def doDict(data_humidity, data_temperature, hour):
	data_dict = []
	for i in range(0, hour):
		data = {}
		data["hour"] =i
		data["temperature"] = data_temperature[i]
		data["humidity"] = data_humidity[i]
		data_dict.append(data)

	return data_dict

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
