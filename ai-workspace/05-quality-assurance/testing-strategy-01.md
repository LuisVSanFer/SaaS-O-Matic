## Auditoría Técnica y Correcciones Post-Generación (Control de Calidad)

Tras ejecutar la primera versión generada por Claude Code y realizar pruebas funcionales de extremo a extremo, se detectaron y corrigieron cuatro defectos técnicos que impedían el funcionamiento correcto o comprometían la integridad de los datos:

### 1. Fallo silencioso en la validación fiscal por orden de campos en Pydantic v2
* **Archivo:** `backend/app/schemas.py`
* **Problema detectado:** La validación de DNI/NIE/CIF estaba implementada con `@field_validator('tax_id')` leyendo `info.data.get('country')`. Como en `CustomerBase` el campo `tax_id` estaba declarado antes que `country`, Pydantic ejecutaba el validador antes de poblar el país, devolviendo siempre cadena vacía y omitiendo la comprobación matemática para clientes de España (`ES`).
* **Solución aplicada:** Se reemplazó la validación cruzada por `@model_validator(mode="after")` en `CustomerCreate`, garantizando que la comprobación del algoritmo oficial español se ejecute una vez validados todos los campos individuales del modelo.

### 2. Bloqueo de peticiones por política CORS entre Frontend y Backend
* **Archivo:** `backend/app/main.py`
* **Problema detectado:** El navegador bloqueaba las llamadas desde el frontend (`localhost:3000`) hacia FastAPI (`localhost:8000`) por ausencia de cabeceras `Access-Control-Allow-Origin`.
* **Solución aplicada:** Se configuró `CORSMiddleware` en la instancia de FastAPI para habilitar la comunicación desde los orígenes locales de desarrollo.

### 3. Dependencia `email-validator` ausente en `requirements.txt`
* **Archivo:** `backend/requirements.txt`
* **Problema detectado:** El uso de `EmailStr` en los esquemas de Pydantic provocaba un `ImportError` al arrancar `uvicorn` porque el paquete `email-validator` no estaba instalado ni congelado en las dependencias.
* **Solución aplicada:** Se instaló `email-validator` en el entorno virtual y se regeneró `requirements.txt` para asegurar la reproducibilidad del entorno en local.

### 4. Petición HTTP redundante en el simulador en tiempo real
* **Archivo:** `frontend/src/services/api.ts`
* **Problema detectado:** La función `simulationApi.preview()` realizaba una llamada previa a `customerApi.getById()` cada vez que el usuario movía el control deslizante, duplicando innecesariamente el tráfico de red pese a que el endpoint `POST /simulations/preview` ya resuelve el país del cliente en servidor.
* **Solución aplicada:** Se eliminó la consulta redundante `getById()` dentro de `preview()`.