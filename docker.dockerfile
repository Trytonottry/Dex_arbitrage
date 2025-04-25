FROM python:3.9-slim

WORKDIR /app
COPY dex_arbitrage.py .
COPY test_arbitrage.py .
COPY .env .

RUN pip install web3 python-dotenv pytest

CMD ["python", "dex_arbitrage.py"]