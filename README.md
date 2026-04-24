![Python](https://img.shields.io/badge/Python-3.x-blue)
![Status](https://img.shields.io/badge/status-complete-success)
![Automation](https://img.shields.io/badge/type-automation-purple)



DESCARGADOR SEP TRIMESTRAL - PYTHON


DESCRIPCIÓN

Este proyecto implementa un sistema automatizado para la descarga masiva de archivos desde páginas trimestrales de la Secretaría de Educación Pública (SEP).

El script navega dinámicamente por la página principal de un trimestre, identifica los enlaces correspondientes a cada estado, accede a sus respectivas secciones y descarga archivos disponibles (ZIP, Excel, PDF), organizándolos automáticamente en una estructura de carpetas.

Este tipo de automatización permite ahorrar tiempo en procesos repetitivos de descarga y organización de información pública.


FUNCIONALIDADES PRINCIPALES

Navegación automatizada con Selenium  
Detección dinámica de enlaces por estado  
Extracción de secciones mediante BeautifulSoup  
Validación de archivos descargables por extensión  
Descarga automática de archivos  
Organización en carpetas por estado y sección  
Manejo básico de errores en carga de páginas  
Detección de finalización de descargas  


TECNOLOGÍAS UTILIZADAS

Python  
Selenium  
BeautifulSoup  
pathlib  
re  
shutil  
time  


FLUJO DEL PROCESO

Apertura del navegador Chrome automatizado  
Acceso a la página del trimestre  
Identificación de enlaces de estados  
Ingreso a cada página estatal  
Extracción de secciones y enlaces  
Validación de archivos descargables  
Descarga de archivos  
Movimiento a carpetas organizadas  
Cierre del navegador  


ESTRUCTURA GENERADA

Ejemplo:

C:/Documents/  
└── Tercer_Trimestre_2015/  
  ├── AGUASCALIENTES/  
  │  ├── Archivo 1/  
  │  └── Archivo 2/  
  ├── PUEBLA/  
  │  ├── Archivo 1/  
  │  └── Archivo 2/  


CONFIGURACIÓN

Modificar las siguientes variables dentro del script:

CHROMEDRIVER_PATH = "RUTA_CHROMEDRIVER"  
OUTPUT_DIR = "RUTA_SALIDA"  
TRIMESTRE_URL = "URL_DEL_TRIMESTRE"  

Extensiones permitidas:

EXTENSIONES_DESCARGABLES = (".zip", ".xls", ".xlsx", ".pdf")


EJECUCIÓN

Ejecutar desde la terminal:

```bash
python descargador_sep_trimestral.py
