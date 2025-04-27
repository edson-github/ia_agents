import sqlite3
import requests
import time
import smtplib
from openai import OpenAI
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

client = OpenAI(api_key=config["openai"]["api_key"])

# e-mail
EMAIL_SENDER = config["email"]["sender"]
EMAIL_PASSWORD = config["email"]["password"]
EMAIL_RECEIVER = config["email"]["receiver"]
SMTP_SERVER = config["email"]["smtp_server"]
SMTP_PORT = config["email"]["smtp_port"]

# bd
DB_PATH = "weather_data.db"
# intervalo de verificação
CHECK_INTERVAL = config["agent"]["check_interval"] 

# coleta dados da API e armazena
def collect_weather_data():
    try:
        response = requests.get("http://127.0.0.1:5001/weather")
        if response.status_code == 200:
            data = response.json()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO weather (temperature, humidity, wind_speed, pressure, storm_risk)
                VALUES (?, ?, ?, ?, ?)
            """, (data["temperature"], data["humidity"], data["wind_speed"], data["pressure"], data["storm_risk"]))
            conn.commit()
            conn.close()
            print("📡 Dados meteorológicos coletados!")
    except Exception as e:
        print("❌ Erro ao coletar dados:", e)

# retorna ultimos 10 registros do tempo
def get_last_10_readings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather ORDER BY timestamp DESC LIMIT 10")
    data = cursor.fetchall()
    conn.close()
    return data

# LLM interpreta dados e gera retorno
def analyze_weather_with_llm(data):
    formatted_data = "\n".join([
        f"Temp: {d[1]}°C, Humidade: {d[2]}%, Vento: {d[3]}km/h, Pressão: {d[4]} hPa, Risco: {d[5]}"
        for d in data
    ])

    prompt = f"""
    Você é um meteorologista IA que analisa dados climáticos e gera alertas personalizados.

    Aqui estão as últimas 10 leituras do clima:
    {formatted_data}

    Sua tarefa:
    1. Identifique se há **mudanças climáticas abruptas ou condições extremas** que justifiquem um alerta.
    2. Se houver risco, explique a situação e dê recomendações.
    3. Se **não houver mudanças climáticas relevantes**, retorne "Nenhum risco identificado."

    **Apenas considere risco se houver grandes variações, como quedas abruptas de temperatura, ventos acima de 25km/h ou pressão abaixo de 980 hPa.**
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# Envia alerta
def send_alert(message):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "⚠️ Alerta Meteorológico!"

    body = f"🚨 Alerta de Clima!\n\n{message}\n\nFique atento e tome as precauções necessárias!"
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📩 Alerta enviado por e-mail!")
    except Exception as e:
        print("❌ Erro ao enviar o e-mail:", e)

# loop do agente
def agent_loop():
    while True:
        collect_weather_data()
        data = get_last_10_readings()
        if data:
            alert_message = analyze_weather_with_llm(data)
            if "nenhum risco" not in alert_message.lower():
                send_alert(alert_message)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    agent_loop()
