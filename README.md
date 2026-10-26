#web_scraping_bcv-usdt
Sistema Python automatizado para rastrear tasas del BCV y Binance (USDT) mediante requests, Playwright y BeautifulSoup. Almacena en SQLite con 4 decimales para BCV y 2 para Binance, calculando automáticamente la brecha cambiaria del precio promedio de compra del USDT entre el precio del BCV (USD) en la BD mediante columnas generadas. Se ejecuta a las 07:00, 13:00 y 21:00 con schedule.

El archivo web_scraping_bcv_usdt_pb.py concentra la lógica principal y el programa completo para realizar la extracción de las tasas cambiarias, en tres horarios determinados por día.

Por otro lado, los archivos ejecutar_script_git.py, funciones_actions.py, requirements.txt y la carpeta .github/workflows conforman la  automatización en GitHub. Su propósito es ejecutar el script de manera remota y programada en la nube, asegurando que la base de datos histórica se mantenga actualizada todos los días en los horarios establecidos.
