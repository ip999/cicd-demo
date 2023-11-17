FROM python:3

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/ranaroussi/yfinance@feature/cookie-and-crumb --no-cache-dir

COPY . /app

ENTRYPOINT [ "python" ]

CMD ["app.py" ]