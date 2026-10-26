# web_scraping_bcv-usdt
Sistema Python automatizado para rastrear tasas del BCV y Binance (USDT) mediante requests, Playwright y BeautifulSoup. Almacena en SQLite con 4 decimales para BCV y 2 para Binance, calculando automáticamente la brecha cambiaria en la BD mediante columnas generadas. Se ejecuta a las 07:00, 13:00 y 21:00 con schedule.
