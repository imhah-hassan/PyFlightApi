import configparser
config = configparser.ConfigParser()
config.read('flightapi.ini')
flight_db=config['Config']['db']
port=config['Config']['port']

