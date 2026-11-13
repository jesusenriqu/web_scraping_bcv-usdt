import requests
import urllib3
import sqlite3
import os
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #borrar error de pag no segura

CARPETA_DESTINO = r"D:\19._Trabajos_de_Programacion\1-. Proyectos_Portafolio\2-. Web Scraping\proyecto de github"

#creas la carpeta automáticamente si aún no existe
os.makedirs(CARPETA_DESTINO, exist_ok=True)

#defines DB_NAME con la ruta absoluta completa
DB_NAME = os.path.join(CARPETA_DESTINO, "tasas_historico_api.db")

def inicializar_base_datos_api():
    #crea la tabla si no existe al iniciar el script
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasas_historico_api (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            usd REAL,
            usdt_compra REAL,
            usdt_venta REAL,
            eur REAL,
            cny REAL,
            rub REAL,
            -- Columna calculada automáticamente
            dif_compra REAL GENERATED ALWAYS AS (ROUND((usdt_compra/usd - 1)*100,4)) STORED,
            dif_venta REAL GENERATED ALWAYS AS (ROUND((usdt_venta/usd - 1)*100,4)) STORED
        )
    """)
    conexion.commit()
    conexion.close()

def guardar_en_bd_api(usd, usdt_compra, usdt_venta, eur, cny, rub):
    #inserta todas las tasas en sus respectivas columnas junto con la fecha-hora
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO tasas_historico_api (fecha_hora, usd, usdt_compra, usdt_venta, eur, cny, rub) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fecha_actual, usd, usdt_compra, usdt_venta, eur, cny, rub))
    conexion.commit()
    conexion.close()
    print(f"[{fecha_actual}] Tasas guardadas correctamente en la base de datos.")

#mediana de precios de compra y venta de USDT/VES en el P2P de Binance:
def obtener_usdt_p2p(url, tipo, filas=11):
    """
    Devuelve la mediana de los precios USDT/VES del P2P de Binance
    tipo:   "BUY": anuncios de gente que VENDE USDT (tú compras)
            "SELL": anuncios de gente que COMPRA USDT (tú vendes)
    """
    #peticion POST a la API de Binance P2P para obtener los anuncios:
    payload = {
        "fiat": "VES",
        "asset": "USDT",
        "tradeType": tipo,
        "page": 1,
        "rows": filas,
        "payTypes": [],
        "countries": [],
        "publisherType": None,
        "proMerchantAds": False,
        "shieldMerchantAds": False,
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    #obtener la lista de anuncios:
    anuncios = r.json().get("data") or []
    #extraer los precios de los anuncios:
    precios = [float(a["adv"]["price"]) for a in anuncios]
    if not precios:
        return None
    #calcular la mediana:
    precios.sort()
    mediana = precios[len(precios) // 2]
    return round(mediana, 4)

def BCV_ACT_API(URL,URL1):
    try:
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"} #simular credenciales de una pc
        r = requests.get(URL, headers=headers, verify=False) #solicitar la info de un url
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser') #buscar informacion dentro del html de la pag
            
            #tasas a buscar
            div_usd = soup.find('div', id='dolar')
            div_eur = soup.find('div', id='euro')
            div_cny = soup.find('div', id='yuan')
            div_rub = soup.find('div', id='rublo')
            
            #convertir a valor con decimal de 4 cifras significativas y en el caso de no encontrar colocar n/a
            usd = round(float(div_usd.get_text(strip=True).strip('USD').replace('.', '').replace(',', '.')),4) if div_usd else None
            eur = round(float(div_eur.get_text(strip=True).strip('EUR').replace('.', '').replace(',', '.')),4) if div_eur else None
            cny = round(float(div_cny.get_text(strip=True).strip('CNY').replace('.', '').replace(',', '.')),4) if div_cny else None
            rub = round(float(div_rub.get_text(strip=True).strip('RUB').replace('.', '').replace(',', '.')),4) if div_rub else None
            
            r.close() #cerrar el requests
        else:
            print(f"Error HTTP URL: {r.status_code}")
        
        #buscar la tasa usdt en binance
        usdt_compra = obtener_usdt_p2p(URL1, "BUY")
        usdt_venta = obtener_usdt_p2p(URL1, "SELL")
        
        #guardar informacion de la n cantidad de tasas
        guardar_en_bd_api(usd, usdt_compra, usdt_venta, eur, cny, rub)
        
    except Exception as e:
        print(f"Ocurrió un error durante el scraping: {e}")