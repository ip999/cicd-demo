import yfinance as yf
from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
redis_ttl = 900

@app.route('/')
def info():
    ticker = request.args.get('ticker')
    stock = yf.Ticker(ticker)
    info = stock.info
    return jsonify(info)

@app.route('/news')
def news():
    ticker = request.args.get('ticker')
    stock = yf.Ticker(ticker)
    news = stock.news
    return jsonify(news)

@app.route('/cached')
def cached():
    ticker = request.args.get('ticker')
    cached_info = cache.get(ticker)
    if cached_info is not None:
        info = json.loads(cached_info)
        # info['x-cache'] = True
    else:
        try: 
            stock = yf.Ticker(ticker)
            cache.set(ticker, json.dumps(stock.info))
            cache.expire(ticker, redis_ttl)
            info = stock.info
            # info['x-cache'] = False
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify(info)

if __name__ == '__main__':
    app.run(host="0.0.0.0")