import configparser
cfg = configparser.ConfigParser()
cfg.read('flightapi.ini')
flight_db=cfg['Config']['db']
port=cfg['Config']['port']

