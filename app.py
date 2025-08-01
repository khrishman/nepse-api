from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# Nepal Time
nepal_tz = pytz.timezone('Asia/Kathmandu')

@app.route('/')
def index():
    return jsonify({"message": "NEPSE API is live!"})

@app.route('/api/stocks')
def get_stocks():
    url = "https://merolagani.com/LatestMarket.aspx"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        rows = soup.select(".normal-row, .increase-row, .decrease-row, .nochange-row")
        data = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 7:
                stock = {
                    "symbol": cols[0].text.strip(),
                    "ltp": cols[1].text.strip(),
                    "percent_change": cols[2].text.strip(),
                    "open": cols[5].text.strip(),
                    "high": cols[3].text.strip(),
                    "low": cols[4].text.strip(),
                    "volume": cols[6].text.strip(),
                    "time": datetime.now(nepal_tz).strftime('%Y-%m-%d %H:%M:%S')
                }
                data.append(stock)

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
    

