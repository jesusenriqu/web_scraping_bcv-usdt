from funciones_actions import BCV_ACT, inicializar_base_datos
from funciones_actions_api import BCV_ACT_API, inicializar_base_datos_api

#Archivo principal
if __name__ == "__main__":
    #crea la tabla si no existe al iniciar el script
    inicializar_base_datos()
    inicializar_base_datos_api()
    
    nurl = ["https://www.bcv.org.ve","https://www.binance.com/es-LA/price/tether/VES","https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"] #n url a usar
    
    #ejecutar el scraping
    BCV_ACT(nurl[0],nurl[1])
    BCV_ACT_API(nurl[0],nurl[2])
