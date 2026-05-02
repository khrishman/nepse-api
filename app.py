from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

nepal_tz = pytz.timezone("Asia/Kathmandu")


@app.route("/")
def index():
    return jsonify({
        "message": "NEPSE API is live!",
        "stocks_endpoint": "/api/stocks"
    })


@app.route("/api/stocks")
def get_stocks():
    url = "https://merolagani.com/LatestMarket.aspx"

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
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
                    "time": datetime.now(nepal_tz).strftime("%Y-%m-%d %H:%M:%S")
                }

                if stock["symbol"]:
                    stocks.append(stock)

        return jsonify({
            "count": len(stocks),
            "updated_at": datetime.now(nepal_tz).strftime("%Y-%m-%d %H:%M:%S"),
            "data": stocks
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Failed to fetch data from Merolagani",
            "details": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "Something went wrong while scraping NEPSE data",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
