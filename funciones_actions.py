import requests
import urllib3
import sqlite3
import time
import random
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #borrar error de pag no segura

#nombre del archivo de base de datos local
DB_NAME = "tasas_historico.db"

def inicializar_base_datos():
    #crea la tabla si no existe al iniciar el script
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasas_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            usd REAL,
            usdt_compra REAL,
            usdt_venta REAL,
            eur REAL,
            cny REAL,
            rub REAL,
            -- Columna calculada automáticamente
            dif REAL GENERATED ALWAYS AS (ROUND((usdt_compra/usd - 1)*100,4)) STORED
        )
    """)
    conexion.commit()
    conexion.close()

def guardar_en_bd(usd, usdt_compra, usdt_venta, eur, cny, rub):
    #inserta todas las tasas en sus respectivas columnas junto con la fecha-hora
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO tasas_historico (fecha_hora, usd, usdt_compra, usdt_venta, eur, cny, rub) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fecha_actual, usd, usdt_compra, usdt_venta, eur, cny, rub))
    conexion.commit()
    conexion.close()
    print(f"[{fecha_actual}] Tasas guardadas correctamente en la base de datos.")

def BCV_ACT(URL,URL1):
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
            usd = round(float(div_usd.get_text(strip=True).strip('USD').replace(',', '.')),4) if div_usd else None
            eur = round(float(div_eur.get_text(strip=True).strip('EUR').replace(',', '.')),4) if div_eur else None
            cny = round(float(div_cny.get_text(strip=True).strip('CNY').replace(',', '.')),4) if div_cny else None
            rub = round(float(div_rub.get_text(strip=True).strip('RUB').replace(',', '.')),4) if div_rub else None
            
            r.close() #cerrar el requests
        else:
            print(f"Error HTTP URL: {r.status_code}")
        
        #buscar la tasa usdt en binance
        with sync_playwright() as p:
            navegador = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            cont = navegador.new_context(user_agent=headers["User-Agent"])
            r1 = cont.new_page()
            r1.goto(URL1)
            time.sleep(random.randint(6, 8))
            
            soup1 = BeautifulSoup(r1.content(), 'html.parser') #buscar informacion dentro del html de la pag
            
            #tasas a buscar
            div_usdt = soup1.find('div', class_='bn-flex flex-col gap-y-2 md:flex-row md:flex-1')
            div_usdt = div_usdt.get_text(separator=" ",strip=True)
            #convertir a valor con decimal de 2 cifras significativas y en el caso de no encontrar colocar n/a
            usdt_compra = round(float(div_usdt.split(" ")[3].replace(",","")),2) if div_usdt else None
            usdt_venta = round(float(div_usdt.split(" ")[8].replace(",","")),2) if div_usdt else None
            
            cont.close() #cerrar el contexto del navegador
            navegador.close() #cerrar el navegador
        
        #guardar informacion de la n cantidad de tasas
        guardar_en_bd(usd, usdt_compra, usdt_venta, eur, cny, rub)
        
    except Exception as e:
        print(f"Ocurrió un error durante el scraping: {e}")
