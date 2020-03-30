from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import csv
from pymongo import MongoClient


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),

}

#Inicialización del grafo DAG de tareas para el flujo de trabajo
dag = DAG(
    'plantila_p2',
    default_args=default_args,
    description='Un grafo simple de tareas',
    schedule_interval=timedelta(days=1),
)

PrepararExterno = BashOperator(
    task_id='PrepararEntorno',
    depends_on_past=False,
    bash_command='mkdir -p /tmp/workflow/',
    dag=dag,
)

CapturaDatosA = BashOperator(
    task_id='CapturarDatosA',
    depends_on_past=False,
    bash_command='wget --output-document /tmp/workflow/humidity.csv.zip https://github.com/manuparra/MaterialCC2020/raw/master/humidity.csv.zip',
    dag=dag,
)

CapturaDatosB = BashOperator(
    task_id='CapturarDatosB',
    depends_on_past=False,
    bash_command='wget --output-document /tmp/workflow/temperature.csv.zip https://github.com/manuparra/MaterialCC2020/raw/master/temperature.csv.zip',
    dag=dag,
)

UnzipDatos = BashOperator(
    task_id='UnzipDatos',
    depends_on_past=False,
    bash_command='unzip -o /tmp/workflow/humidity.csv.zip -d /tmp/workflow/ && unzip -o /tmp/workflow/temperature.csv.zip -d /tmp/workflow/',
    dag=dag,
)

def procesarDatos(ds, **kwargs):
	with open('/tmp/workflow/humidity.csv') as csvhumidity, open('/tmp/workflow/temperature.csv') as csvtemperature:
		readerH = csv.DictReader(csvhumidity)
		readerT = csv.DictReader(csvtemperature)
		data_dict = {}
		data_dict['datetime'] = []
		data_dict['temperature'] = []
		data_dict['humidity'] = []
		for rowT in readerT:
			data_dict['datetime'].append(rowT['datetime'])
			if (rowT['San Francisco'] == ''):
				data_dict['temperature'].append(0)
			else:
				data_dict['temperature'].append(rowT['San Francisco'])

		for rowH in readerH:
			if (rowT['San Francisco'] == ''):
				data_dict['humidity'].append(0)
			else:
				data_dict['humidity'].append(rowH['San Francisco'])

		mongo_client=MongoClient('mongodb://127.0.0.1:27017/')
		db=mongo_client.cc
		collection = db.prediction
		collection.drop()
		collection.insert_one({'index':'SF', 'datos':data_dict})
	

ProcesarDatos = PythonOperator(
    task_id='ProcesaDatos',
    provide_context=True,
    python_callable=procesarDatos,
    dag=dag,
)	

ClonarRepo = BashOperator(
    task_id='ClonarRepo',
    depends_on_past=False,
    bash_command='rm -r -f /tmp/workflow/repository && git clone https://github.com/manuelalonsobraojos/cc2-airflow.git /tmp/workflow/repository',
    dag=dag,
)

V1Build = BashOperator(
    task_id='V1Build',
    depends_on_past=False,
    bash_command='cd /tmp/workflow/repository && docker-compose build api_v1',
    dag=dag,
)

V2Build  = BashOperator(
    task_id='V2Build',
    depends_on_past=False,
    bash_command='cd /tmp/workflow/repository && docker-compose build api_v2',
    dag=dag,
)

V1Up = BashOperator(
    task_id='V1Up',
    depends_on_past=False,
    bash_command='cd /tmp/workflow/repository && docker-compose up -d api_v1',
    dag=dag,
)

V2Up = BashOperator(
    task_id='V2Up',
    depends_on_past=False,
    bash_command='cd /tmp/workflow/repository && docker-compose up -d api_v2',
    dag=dag,
)

MongoContainerBuild = BashOperator(
    task_id='MongoContainerBuild',
    depends_on_past=True,
    bash_command='cd /tmp/workflow/repository && docker-compose build mongo',
    dag=dag,
)

MongoContainerUp = BashOperator(
    task_id='MongoContainerUp',
    depends_on_past=True,
    bash_command='cd /tmp/workflow/repository && docker-compose up -d mongo',
    dag=dag,
)

Testing = BashOperator(
    task_id='MongoContainerUp',
    depends_on_past=True,
    bash_command='cd /tmp/workflow/repository && python3 test.py',
    dag=dag,
)

#Dependencias
PrepararExterno >> [CapturaDatosA, CapturaDatosB, ClonarRepo] >> UnzipDatos >> [MongoContainerBuild, V1Build, V2Build]  >> MongoContainerUp >> ProcesarDatos >> [V1Up, V2Up] >> Testing


