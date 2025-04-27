from flask import Flask, jsonify, request
import random
import argparse

# sem tempestade python weather_api.py
# com tempestade python weather_api.py --storm
parser = argparse.ArgumentParser(description="Iniciar com simulação de tempestade.")
parser.add_argument("--storm", action="store_true", help="Ativar simulação de tempestade.")
args = parser.parse_args()

app = Flask(__name__)

# Flag para simular tempestades
simulate_storm = args.storm  


@app.route('/weather', methods=['GET'])
def get_weather():
    global simulate_storm

    if simulate_storm:
        # Dados de tempestade
        data = {
            "temperature": round(random.uniform(5, 15), 1),  # temperatura
            "humidity": random.randint(80, 100),  # umidade
            "wind_speed": round(random.uniform(25, 40), 1),  # ventos
            "pressure": round(random.uniform(970, 985), 1),  # pressão
            "storm_risk": True  # risco
        }
    else:
        # normal, variações pequenas
        base_temperature = 25.0  
        base_wind_speed = 10.0  
        base_pressure = 1013.0  

        data = {
            "temperature": round(base_temperature + random.uniform(-0.5, 0.5), 1), 
            "humidity": random.randint(40, 60),  
            "wind_speed": round(base_wind_speed + random.uniform(-1, 1), 1), 
            "pressure": round(base_pressure + random.uniform(-1, 1), 1),  
            "storm_risk": False  
        }

    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
