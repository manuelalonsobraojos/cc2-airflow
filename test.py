import unittest
import requests

class ResultTest(unittest.TestCase):

	def test_response_api_v2(self):
		URL = "http://127.0.0.1:5001/servicio/v2/prediccion/24horas/"
		r = requests.get(url = URL) 
		data = r.json()
		self.assertTrue(r.status_code == 200)

	def test_data_api_v2(self):
		URL = "http://127.0.0.1:5001/servicio/v2/prediccion/48horas/"
		r = requests.get(url = URL) 
		data = r.json()
		print(type(data))
		self.assertTrue(type(data) == list)
	
	def test_api_v1(self):
		URL = "http://127.0.0.1:5000/servicio/v1/prediccion/24horas/"
		r = requests.get(url = URL) 
		data = r.json()
		self.assertTrue(r.status_code == 200)

	def test_data_api_v1(self):
		URL = "http://127.0.0.1:5000/servicio/v1/prediccion/24horas/"
		r = requests.get(url = URL) 
		data = r.json()
		print(type(data))
		self.assertTrue(type(data) == list)

if __name__ == '__main__':
   unittest.main()



