This services currently available for two categories of Forex and cryptocurrency markets and also four currency pairs of [ EUR_USD , USD_JPY , GBP_USD , BTC_USDT] based on resolution 60 minutes.
We schedule our prediction services every hours in business days and POST the predicted values to our Mongo engine services.

After data preparation and model prediction, we POST predicted price into our mongoengine services and we have following attributes:

| Attribute | Description | Example | Null |
|-----------|-------------|--------|--------|
|   Category      | currency pair category     |Forex or cryptocurrency |No|
|   pair   | currency pair symbol |  EURUSD  |No|
|   timestamp   | UNIX UTC timestamp |  1615513000  |No|
|   resolution   | model trained and used based on this resolution |  60 (an hour) |No|
|   predictedPrice   | predicted price value corresponding to timestamp | 1.181719  |No|
