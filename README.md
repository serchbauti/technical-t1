# T1 Technical Test API

API asincrónica construida con FastAPI para gestionar clientes, tarjetas y cargos dentro de un flujo de pagos de prueba. El proyecto está containerizado, integra MongoDB como base de datos operativa y expone documentación automática vía OpenAPI.

## Alcance
- Incluye CRUD de clientes y tarjetas, creación de cargos con historial y reembolsos simulados, además de health-check.


## Stack Tecnológico
- **Python 3.12** con **FastAPI** y **Uvicorn** para la capa HTTP.
- **MongoDB 7** con **Beanie** (ODM sobre Motor) para acceso asíncrono a datos.
- **Pydantic v2** para validación y serialización de esquemas.
- **Docker** y **Docker Compose** para un entorno reproducible.
- **Pytest**, **pytest-asyncio** y **httpx** para pruebas unitarias e integrales.
- **Postman** para invocar y automatizar validaciones manuales mediante colección exportada.

## Arquitectura y Diseño
- Separación en capas (`domain`, `infrastructure`, `http`) siguiendo principios de clean architecture.
- Lógica crítica de tarjetas encapsulada en reglas de dominio (`luhn.py`) con pruebas unitarias dedicadas.
- ODM Beanie define `Document` con índices para búsquedas eficientes e idempotencia por `request_id`.
- Ciclo de vida de FastAPI inicializa y cierra la conexión a Mongo en el `lifespan` de la aplicación.
- Tests integran fixtures que limpian la base durante cada escenario para evitar dependencias cruzadas.

## Estructura del Repositorio
```
/app
  /domain          # Entidades y reglas de negocio (Luhn, reglas de validación)
  /http            # Routers FastAPI y esquemas Pydantic
  /infrastructure  # Persistencia con Beanie/Mongo
  main.py          # Punto de entrada FastAPI con routers y lifespan
/tests             # Unitarias e integraciones con pytest
/scripts           # Utilidades (espera activa para Mongo)
Dockerfile         # Imagen de la API
docker-compose.yml # Orquestación API + Mongo
Makefile           # Comandos abreviados para build/run/test
postman/           # Colección Postman exportada
```

## Configuración del Entorno
- Clonar el repositorio y ubicarse en `/Users/sergioperez/technical-t1`.
- Copiar la configuración base: `cp env.example .env`.
- Editar `.env` si se requiere un URI distinto de Mongo (`MONGODB_URI`).

## Makefile
- `make build`: construye la imagen Docker de la API.
- `make up`: levanta API y Mongo en segundo plano (crea `.env` si falta).
- `make down`: detiene y limpia los contenedores.
- `make logs`: muestra logs en vivo del servicio `api`.
- `make test`: ejecuta las pruebas dentro del contenedor de la API (espera a Mongo previamente).

## Puesta en Marcha con Docker
1. **Build opcional**: `make build`.
2. **Levantar servicios**: `make up`. Se crea `.env` si no existe, monta la app en modo recarga y expone:
   - API FastAPI en `http://localhost:8000`
   - MongoDB en `mongodb://localhost:27017`
3. **Logs en vivo**: `make logs`.
4. **Apagar servicios**: `make down`.

## Documentación y Rutas Clave
- Documentación OpenAPI: `http://localhost:8000/docs`.
- Health check: `GET http://localhost:8000/health`.
- Recursos principales:
  - `POST /clients`, `GET /clients/{id}`, `PUT /clients/{id}`, `DELETE /clients/{id}`.
  - `POST /cards`, `GET /cards/{id}`, `PUT /cards/{id}`, `DELETE /cards/{id}`.
  - `POST /charges`, `GET /charges/{client_id}`, `POST /charges/{id}/refund`.

## Colección de Postman
- Archivo: `postman/T1_Technical_API.son` (colección v2.1).
- Importar desde Postman: **File → Import → Upload Files** y seleccionar el archivo.
- La colección incluye scripts que guardan `clientId`, `cardId` y `chargeId` en el environment activo.

## Pruebas con Makefile
- `make test` ejecuta toda la suite (`pytest`) dentro del contenedor, ideal para entornos homogéneos.


## Pruebas Automatizadas
- **Unitarias (`tests/unit`)**: cubren utilidades de la regla de Luhn (generación y validación de PAN). Se ejecutan rápido y verifican la lógica pura.
- **Integración (`tests/integration`)**: validan flujos completos sobre la API expuesta por FastAPI usando `TestClient`.
  - Clientes: altas, consultas, actualización parcial y borrado.
  - Tarjetas: creación con validación Luhn, actualización de bin/last4 y borrado.
  - Cargos: aprobación, declinación por reglas de negocio (últimos 4 dígitos o monto), idempotencia y filtros de listado.
- Puedes lanzarlas con `make test` para ejecutar dentro del contenedor Docker.

## Escenario de pruebas

## Crear **clients**

### Endpoint
`POST /clients`

### Request body (schema)
| Campo | Tipo | Requerido | Validación |
|------:|------|:---------:|-----------|
| `name`  | string  | ✓ | longitud 1–120 |
| `email` | string (Email) | ✓ | formato de email válido |
| `phone` | string | ✗ | máx. 30 caracteres |

> **Nota:** por defecto **no** se fuerza unicidad de `email` a nivel de DB.

## Crear tarjetas de prueba (solo para crear; la API nunca almacena el PAN completo)

### Endpoint
`POST /cards`

| Alias | BIN    | PAN de prueba (Luhn válido) | last4 | Regla aplicada |
|------:|--------|------------------------------|:-----:|----------------|
| Card A (OK) | 411111 | 4111111111111111         | 1111 | Aprobado por defecto (si monto ≤ 5000) |
| Card B (bloqueada) | 424242 | 4242424242420000   | 0000 | **Rechazo** por patrón de PAN (`SUSPECT_PAN`) |
| Card C (bloqueada) | 410000 | 4100000000059999   | 9999 | **Rechazo** por patrón de PAN (`SUSPECT_PAN`) |
| Card D (OK) | 555555 | 5555555555554444         | 4444 | Aprobado por defecto (si monto ≤ 5000) |

> Nota: Usa estos PAN **solo** en `POST /cards`. Después, la API trabaja con IDs.

## Crear cargos a tarjetas

### Endpoints
- `POST /charges` — crear un cobro simulado (con **idempotencia** vía `request_id`)
- `POST /charges/{charge_id}/refund` — reembolsar un cobro **aprobado**

---

### **Reglas de decisión**
- **Blacklist por `last4`**: `0000` o `9999` → `status="declined"`, `reason_code="SUSPECT_PAN"`.
- **Límite de monto**: `amount > 5000` → `status="declined"`, `reason_code="LIMIT_EXCEEDED"`.
- Caso contrario → `status="approved"`.

---

### `POST /charges` (crear cargo)
**Headers**
- `Content-Type: application/json`

**Request body (schema)**
| Campo        | Tipo    | Req. | Detalle |
|-------------:|---------|:----:|---------|
| `client_id`  | string  |  ✓   | ObjectId del cliente existente |
| `card_id`    | string  |  ✓   | ObjectId de la tarjeta del cliente |
| `amount`     | number  |  ✓   | `> 0` (p. ej. `100`) |
| `request_id` | string  |  ✗   | **Idempotencia**: UUID por intento (mismo valor en reintento) |


---

## Escenarios de validación

1) **Aprobado por defecto**  
   - **Tarjeta**: *Card A* (`…1111`)  
   - **Monto**: `100`  
   - **Esperado**: `status="approved"`, `reason_code=null`.

2) **Rechazado por monto**  
   - **Tarjeta**: *Card A* (`…1111`)  
   - **Monto**: `6000`  
   - **Esperado**: `status="declined"`, `reason_code="LIMIT_EXCEEDED"`.

3) **Rechazado por patrón de PAN**  
   - **Tarjeta**: *Card B* (`…0000`) **o** *Card C* (`…9999`)  
   - **Monto**: `100`  
   - **Esperado**: `status="declined"`, `reason_code="SUSPECT_PAN"`.

4) **Reembolso sobre cargo aprobado (usando tarjeta `…1111`)**  
   - **Tarjeta**: *Card A* (`…1111`)  
   - **Flujo**: crear cargo → `POST /charges/{id}/refund`, se proporciona el id del cargo a refondear
   - **Esperado**: respuesta de refund con `refunded=true` y `refunded_at` con timestamp.

## Contacto
- Sergio Pérez Bautista — `perez.sergiob@gmail.com`


