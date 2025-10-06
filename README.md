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

## Pruebas Automatizadas
- Dentro de Docker: `make test` (ejecuta `pytest` tras esperar a Mongo).
- Local sin Docker: asegurarse de tener Mongo disponible y lanzar `pytest`.
- Suite integrada cubre reglas de Luhn, flujo CRUD de clientes, tarjetas y cargos.

## Contacto
- Sergio Pérez Bautista — `perez.sergiob@gmail.com`


