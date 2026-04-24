######
# DESCARGADOR SEP TRIMESTRAL
# Objetivo: Automatizar la descarga de archivos trimestrales desde una pagina de la SEP,
# detectando estados, secciones y archivos descargables para organizarlos en carpetas.
# Fecha modificacion: 24/04/2026
# Autor: Jorge Fernando Ortiz Bravo
######


import re
import time
import shutil
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, WebDriverException


######
# CONFIGURACION
######

CHROMEDRIVER_PATH = Path(r"C:\Drivers\chromedriver.exe")

OUTPUT_DIR = Path(
    r"C:\Users\Usuario\Documents\DOCUMENTOS_SEP_TRIMESTRALES\Tercer_Trimestre_2015"
)

TRIMESTRE_URL = "https://sep.gob.mx/es/sep1/TERCER_TRIMESTRE_2015"

EXTENSIONES_DESCARGABLES = (".zip", ".xls", ".xlsx", ".pdf")


######
# FUNCIONES GENERALES
######

# Limpia nombres para que puedan usarse como carpetas o archivos en Windows
def normalizar_nombre(nombre: str) -> str:
    nombre = nombre.replace("/", " - ")
    nombre = re.sub(r"[\\:*?\"<>|]", "", nombre)
    return nombre.strip()


# Valida si un enlace pertenece a un archivo descargable
def es_archivo_descargable(href: str) -> bool:
    if not href:
        return False

    href = href.lower().split("?")[0]
    return any(href.endswith(extension) for extension in EXTENSIONES_DESCARGABLES)


# Abre una URL con manejo basico de errores y tiempo de espera
def abrir_url(driver, url: str, intentos: int = 2, timeout: int = 30) -> bool:
    for _ in range(intentos):
        try:
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            return True

        except TimeoutException:
            try:
                driver.execute_script("window.stop();")
                return True
            except Exception:
                pass

        except WebDriverException:
            time.sleep(1)

    return False


# Configura e inicia Chrome
def iniciar_driver():
    opciones = ChromeOptions()
    opciones.add_argument("--window-size=1500,900")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--lang=es-MX")

    preferencias = {
        "download.default_directory": str(OUTPUT_DIR.resolve()),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }

    opciones.add_experimental_option("prefs", preferencias)

    servicio = ChromeService(str(CHROMEDRIVER_PATH))
    return webdriver.Chrome(service=servicio, options=opciones)


# Convierte el HTML actual del navegador en objeto BeautifulSoup
def obtener_soup(driver):
    return BeautifulSoup(driver.page_source, "html.parser")


######
# BUSQUEDA DE ENLACES
######

# Encuentra enlaces de estados dentro de la pagina trimestral
def encontrar_estados(sopa):
    estados = {}

    for enlace in sopa.select("p > a[href]"):
        texto = enlace.get_text(" ", strip=True)
        href = enlace.get("href", "").strip()

        if not texto or not href:
            continue

        if re.search(r"_[1234]$", href.split("/")[-1].upper()):
            url_absoluta = urljoin(TRIMESTRE_URL, href)
            estados[texto] = url_absoluta

    return estados


# Encuentra secciones o archivos dentro de la pagina de cada estado
def encontrar_secciones(sopa, url_base: str):
    secciones = {}

    for enlace in sopa.select("p > a[href]"):
        texto = enlace.get_text(" ", strip=True)
        href = enlace.get("href", "")

        if not href:
            continue

        url_absoluta = urljoin(url_base, href)
        secciones[normalizar_nombre(texto)] = url_absoluta

    return secciones


######
# DESCARGA DE ARCHIVOS
######

# Espera hasta que Chrome termine una descarga
def esperar_descarga(carpeta: Path, archivos_previos: set, timeout: int = 300) -> Path:
    inicio = time.time()

    while time.time() - inicio < timeout:
        archivos_actuales = {archivo for archivo in carpeta.glob("*") if archivo.is_file()}
        archivos_nuevos = archivos_actuales - archivos_previos

        for archivo in archivos_nuevos:
            nombre = archivo.name.lower()

            if nombre.endswith(".crdownload") or nombre.endswith(".tmp"):
                continue

            time.sleep(0.5)
            return archivo

        time.sleep(1)

    raise TimeoutError("La descarga tardó demasiado y no se generó archivo final.")


# Descarga un archivo y lo mueve a su carpeta correspondiente
def descargar_archivo(driver, url: str, destino: Path) -> str | None:
    destino.mkdir(parents=True, exist_ok=True)

    carpeta_base = OUTPUT_DIR.resolve()

    archivos_previos = {
        archivo for archivo in carpeta_base.glob("*")
        if archivo.is_file() and not archivo.name.endswith((".tmp", ".crdownload"))
    }

    ventana_principal = driver.current_window_handle

    driver.execute_script("window.open('about:blank','_blank');")
    nueva_ventana = [ventana for ventana in driver.window_handles if ventana != ventana_principal][0]
    driver.switch_to.window(nueva_ventana)

    if not abrir_url(driver, url):
        driver.close()
        driver.switch_to.window(ventana_principal)
        return None

    try:
        archivo_descargado = esperar_descarga(carpeta_base, archivos_previos)
        ruta_final = destino / archivo_descargado.name

        shutil.move(str(archivo_descargado), str(ruta_final))

        print(f"Descargado: {ruta_final}")

        driver.close()
        driver.switch_to.window(ventana_principal)

        return str(ruta_final)

    except Exception:
        driver.close()
        driver.switch_to.window(ventana_principal)
        return None


######
# PROCESO PRINCIPAL
######

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    driver = iniciar_driver()

    print("Chrome iniciado.")
    print("Abriendo pagina trimestral...")

    if not abrir_url(driver, TRIMESTRE_URL, intentos=3):
        print("No se pudo abrir la pagina trimestral.")
        driver.quit()
        return

    sopa = obtener_soup(driver)
    estados = encontrar_estados(sopa)

    print(f"Estados detectados: {len(estados)}")

    if not estados:
        print("No se detecto ningun estado. Revisar estructura HTML.")
        driver.quit()
        return

    for estado, enlace_estado in estados.items():
        print(f"\nProcesando estado: {estado}")

        if not abrir_url(driver, enlace_estado):
            print("No se pudo abrir la pagina del estado.")
            continue

        sopa_estado = obtener_soup(driver)
        secciones = encontrar_secciones(sopa_estado, enlace_estado)

        for nombre_seccion, enlace in secciones.items():
            print(f"Seccion: {nombre_seccion}")

            destino = OUTPUT_DIR / estado / nombre_seccion

            if es_archivo_descargable(enlace):
                descargar_archivo(driver, enlace, destino)
            else:
                print("No es archivo descargable.")

    driver.quit()


######
# EJECUCION
######

if __name__ == "__main__":
    main()