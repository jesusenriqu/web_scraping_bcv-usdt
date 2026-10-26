import asyncio
from web_scraping_bcv_usdt_pb import BCV_ACT, inicializar_base_datos

#Archivo principal
if __name__ == "__main__":
    #crea la tabla si no existe al iniciar el script
    inicializar_base_datos()
    
    nurl = ["https://www.bcv.org.ve","https://www.binance.com/es-LA/price/tether/VES"] #n url a usar
    
    #ejecutar el scraping de forma asíncrona una sola vez
    asyncio.run(BCV_ACT(nurl[0],nurl[1]))