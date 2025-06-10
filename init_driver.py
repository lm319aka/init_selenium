# import os

# from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

import chromedriver_autoinstaller

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support import expected_conditions as ec
# from selenium.common.exceptions import *

# from fake_useragent import UserAgent
import undetected_chromedriver as uc

# from private import env_vars
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MIN = "min"
MAX = "max"

SPANISH = ("es-ES", "es")
ENGLISH_USA = ("en", "en_US")


class LangLabel:

    def __init__(self, lang: str):
        self.lang: str = lang

    def ret(self):
        with open("driver_info/langs.json", "r", encoding="utf-8") as lang_file:
            lang_env_file = json.load(lang_file)
        lang_file_dict: dict = lang_env_file["langs"]
        try:
            lang_label: str = lang_file_dict["langs"][self.lang]
        except KeyError:
            raise KeyError(f"{self.lang} does not exists")
        else:
            lang_from_env: str
            if "," in lang_label:
                lang_from_env = lang_label.strip()[:lang_label.index(",")]
            else:
                lang_from_env = lang_label.strip()
            return lang_from_env, lang_from_env


def download_chrome_driver() -> str:
    chromedriver_filepath = chromedriver_autoinstaller.install()
    return chromedriver_filepath


def create_driver(drivers_route: str = None,
                  user_agent: str = None,
                  window_size: str = "max",
                  window_position: tuple[int, int] = (0, 0),
                  sand_box: bool = False,
                  wait_time: int = 20,
                  manage_notificaions: int = 2,
                  language: tuple[str, str] = SPANISH,
                  save_psw: bool = False,
                  camuflate: bool = True,
                  disable_web_security: bool = True,
                  install: bool = False,
                  undetectable: bool = False,
                  cookies: dict[str, str] = None,
                  initial_url: str = None) -> tuple[webdriver.Chrome, WebDriverWait]:

    if manage_notificaions not in [0, 1, 2]:
        raise ValueError(f"there is not a notification level {manage_notificaions}")

    if install or not drivers_route:
        drivers_route = download_chrome_driver()

    driver_manager = Service(drivers_route)
    options = Options()

    num_win_size = (None, None)

    match window_size:
        case "max":
            options.add_argument("--start-maximized")  # maximizar ventana
        case "min":
            options.add_argument("--headless")  # ejecutar chrome sin abrir ventana
        case _:
            if "x" in window_size:
                try:
                    alto, ancho = window_size.split("x")
                    if alto and ancho:
                        # options.add_argument(f"--window-size={alto},{ancho}")  # alto y ancho de ventana
                        num_win_size = (int(alto), int(ancho))
                    else:
                        raise ValueError("wrong value/s")
                except ValueError:
                    raise ValueError("more or less than 2 values")
            else:
                raise ValueError(f"error with window size: {window_size}")

    options.add_argument(f"user-agent={user_agent}")  # define un user agent
    if disable_web_security:
        options.add_argument("--disable-web-security")  # deshabilita la política del mismo origen

    options.add_argument("--disable-extensions")  # que no cargue las extensiones de chrome
    options.add_argument("--disable-notifications")  # bloquear notificaciones chrome
    options.add_argument("--ignore-certificate-errors")  # ignorar aviso de "su conexion no es privada"

    if not sand_box:
        options.add_argument(
            "--no-sandbox")  # “No-sandbox” es una opción que se puede usar en el navegador Google Chrome para deshabilitar el sandbox.
    # El sandbox es un mecanismo de seguridad que se utiliza para aislar los procesos del navegador y evitar que los sitios web maliciosos ejecuten código en el equipo del usuario.
    # Al deshabilitar el sandbox, se expone al usuario a posibles exploits de JavaScript maliciosos que pueden ejecutar código arbitrario en su equipo.
    options.add_argument("--log-level=3")  # para que chrome no muestre nada en terminal
    options.add_argument("--allow-running-insecure-content")  # desactiva aviso de "contenido inseguro"
    options.add_argument("--no-default-browser-check")  # evita que chrome compruebe que no es el navegador por defecto
    options.add_argument("--no-first-run")  # evita la ejecución de
    # ciertas tareas que se realizan la primera vez que se ejecuta chrome
    options.add_argument("--no-proxy-server")  # usar conexiones directas
    if camuflate:
        options.add_argument("--disable-blink-features=AutomationControlled")  # evita que selenium sea detectado
    # options.add_argument("")  # def
    #  PARAMETROS A OMITIR EN EL INICIO DE CHROMEDRIVER
    ext_opt = [
        "enable-automation",  # no se muestra notificación "Un software automatizado de pruebas está controlando chrome"
        "ignore-certificate-errors",  # ignorar errores de certificados
        "enable-logging"  # para que no aparezcan cosas en terminal ("DevTools listening on...")
    ]
    options.add_experimental_option("excludeSwitches", ext_opt)
    #  PARAMETROS PREFERENCIAS DE CHROMEDRIVER
    prefs = {
        "profile.default_content_setting_values.notifications": manage_notificaions,
        # notificaciones: 0=preguntar, 1=permitir, 2=no permitir
        "intl.accept_languages": list(language),  # definir idioma navegador
        "credentials_enable_service": save_psw  # evitar que chrome guarde contraseña
    }
    options.add_experimental_option("prefs", prefs)

    if undetectable:
        options.add_argument("user-data-dir=./")
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # options.add_argument(f"--window-size={num_win_size[0]},{num_win_size[1]}")  # alto y ancho de ventana

        dr = uc.Chrome(chrome_options=options, driver_executable_path=drivers_route)

        # if window_size == "min":
        #     dr.headless = True
    else:
        dr = webdriver.Chrome(service=driver_manager, options=options)

    if any(num_win_size):
        dr.set_window_size(num_win_size[0], num_win_size[1])
        dr.set_window_position(window_position[0], window_position[1])  # posición en pantalla
    wt = WebDriverWait(dr, wait_time)

    if initial_url is not None:
        dr.get(initial_url)

    if cookies is not None:
        for cookie in cookies:
            dr.add_cookie(cookie)

    return dr, wt


if __name__ == "__main__":
    # para instalar el chromedriver automaticamente
    # chromedriver_autoinstaller.install(path=DRIVERS_ROUTE)

    # Example code
    driver, wait = create_driver(window_size=MAX)
    driver.get("https://www.google.com/")
    input("Press Enter to continue...")
    driver.quit()
