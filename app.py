from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
CORS(app)

nepal_tz = pytz.timezone("Asia/Kathmandu")

cached_data = None
last_fetch_time = None
CACHE_SECONDS = 10


@app.route("/")
def index():
    return jsonify({
        "message": "NEPSE API is live!",
        "stocks_endpoint": "/api/stocks"
    })


@app.route("/api/stocks")
def get_stocks():
    global cached_data, last_fetch_time

    now = datetime.now(nepal_tz)

    if cached_data is not None and last_fetch_time is not None:
        if now - last_fetch_time < timedelta(seconds=CACHE_SECONDS):
            return jsonify({
                "source": "cache",
                "count": len(cached_data),
                "updated_at": last_fetch_time.strftime("%Y-%m-%d %H:%M:%S"),
                "data": cached_data
            })

    url = "https://merolagani.com/LatestMarket.aspx"

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select(".normal-row, .increase-row, .decrease-row, .nochange-row")

        stocks = []

        for row in rows:
            cols = row.find_all("td")

            if len(cols) >= 7:
                stock = {
                    "symbol": cols[0].get_text(strip=True),
                    "ltp": cols[1].get_text(strip=True),
                    "percent_change": cols[2].get_text(strip=True),
                    "high": cols[3].get_text(strip=True),
                    "low": cols[4].get_text(strip=True),
                    "open": cols[5].get_text(strip=True),
                    "volume": cols[6].get_text(strip=True),
                    "time": now.strftime("%Y-%m-%d %H:%M:%S")
                }

                if stock["symbol"]:
                    stocks.append(stock)

        cached_data = stocks
        last_fetch_time = now

        return jsonify({
            "source": "live",
            "count": len(stocks),
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "data": stocks
        })

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch NEPSE data",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
