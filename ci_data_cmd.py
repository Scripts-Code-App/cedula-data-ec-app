import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

URL = "https://ecuconsultas.com/personas/consultar-fecha-nacimiento/"

def cerrar_pestañas_publicidad(driver, ventana_principal):
    for handle in driver.window_handles:
        if handle != ventana_principal:
            driver.switch_to.window(handle)
            try:
                driver.close()
            except:
                pass
    driver.switch_to.window(ventana_principal)

def consultar_cedula(ci):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")

    service = Service("./chromedriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(URL)
        ventana_principal = driver.current_window_handle

        input_ci = wait.until(EC.element_to_be_clickable((By.ID, "cedulaInput")))
        input_ci.clear()
        input_ci.send_keys(ci)

        btn = driver.find_element(By.CSS_SELECTOR, "form#searchForm button[type='submit']")
        driver.execute_script("arguments[0].click();", btn)

        time.sleep(1)
        if len(driver.window_handles) > 1:
            cerrar_pestañas_publicidad(driver, ventana_principal)

        wait.until(EC.visibility_of_element_located((By.ID, "resultsSection")))

        def obtener_campo(label_texto):
            try:
                xpath = f"//div[@class='result-field'][.//label[normalize-space()='{label_texto}']]//span[contains(@class,'field-value')]"
                return driver.find_element(By.XPATH, xpath).text.strip()
            except NoSuchElementException:
                return ""

        cedula = obtener_campo("Cédula:")
        nombre = obtener_campo("Nombres completos:")
        fecha_larga = obtener_campo("Fecha de nacimiento:")

        try:
            fecha_corta = driver.find_element(
                By.XPATH,
                "//div[@class='result-field'][.//label[normalize-space()='Fecha de nacimiento:']]//small"
            ).text.strip().replace("(", "").replace(")", "")
        except NoSuchElementException:
            fecha_corta = ""

        try:
            edad = obtener_campo("Edad actual:")
        except:
            edad = ""

        if not cedula:
            return None, None, None, None, None

        return cedula, nombre, fecha_larga, fecha_corta, edad

    except TimeoutException:
        return None, None, None, None, None
    except Exception:
        return None, None, None, None, None
    finally:
        driver.quit()

if __name__ == "__main__":
    while True:
        cedula = input("\nIngresa la cédula: ").strip()

        if cedula.lower() == "salir":
            break

        if not cedula.isdigit() or len(cedula) != 10:
            print("Cédula incorrecta (10 dígitos numéricos).")
            continue

        c, n, f_texto, f_iso, edad = consultar_cedula(cedula)

        if c:
            print(f"Cédula: {c}")
            print(f"Nombres: {n}")
            print(f"Fecha Larga: {f_texto}")
            print(f"Fecha Corta: {f_iso}")
            print(f"Edad: {edad}")
        else:
            print("No se encontró información.")
