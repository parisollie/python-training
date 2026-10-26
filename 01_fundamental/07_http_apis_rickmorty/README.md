# Módulo 07 — HTTP y consumo de APIs (Rick and Morty)

## Objetivos
- Construir clientes HTTP robustos
- Gestionar resiliencia (reintentos, timeouts)
- Consumir APIs REST de forma eficiente
- Manejar streaming para respuestas grandes

## Contenidos clave

### Librerias HTTP en Python
- **requests**: la clasica, sincrona, muy popular
- **httpx**: moderna, sincrona y asincrona, HTTP/2
- **aiohttp**: asincrona pura, mas compleja
- **urllib**: la de la stdlib, basica

Para este modulo usamos **httpx** porque:
- API moderna y consistente (sync y async)
- Soporte de HTTP/2
- Type hints completos
- Streaming eficiente
- Facil de testear con MockTransport

### Timeouts
- Nunca dejar sin timeout (la app se cuelga)
- httpx.Timeout(connect, read, write, pool)
- Configurar por request o por cliente

### Reintentos
- Errores transitorios (5xx, timeouts, conexion)
- NO reintentar errores del cliente (4xx)
- Backoff exponencial
- Libreria: tenacity (o implementacion manual)

### Manejo de errores HTTP
- httpx.HTTPError: base de todos los errores
- httpx.ConnectError: no se pudo conectar
- httpx.TimeoutException: se agoto el tiempo
- httpx.HTTPStatusError: 4xx/5xx (con raise_for_status)
- httpx.RequestError: fallo en la request

### Codigos de estado
- 2xx: OK (200, 201, 204)
- 3xx: redireccion (301, 302, 304)
- 4xx: error del cliente (400, 401, 403, 404, 422, 429)
- 5xx: error del servidor (500, 502, 503, 504)

### Streaming
- Para respuestas grandes: no cargar todo en memoria
- client.stream("GET", url) + iter_bytes / iter_lines / iter_text
- Escribir a disco por chunks
- Muy util para descargas grandes

### APIs REST
- GET: leer
- POST: crear
- PUT: reemplazar
- PATCH: modificar parcialmente
- DELETE: eliminar
- Headers: Content-Type, Accept, Authorization
- Query params: ?key=value&otro=mas

## Laboratorio

Cliente HTTP para la API de Rick and Morty:

1. Cliente httpx sincrono con timeouts
2. Reintentos con backoff exponencial
3. Obtencion de personajes por ID
4. Paginacion (recorrer todas las paginas)
5. Streaming de la respuesta completa a disco
6. Manejo robusto de errores

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Simple es mejor que complejo" -> httpx.Client, no requests + urllib3 + wrappers
- "Explícito es mejor que implícito" -> timeouts explicitos
- "Los errores nunca deben pasar silenciosamente" -> raise_for_status() + manejo

### Cuando usar cada libreria HTTP

| Libreria | Cuando usar |
|----------|-------------|
| requests | Scripts simples, codigo legacy |
| httpx | APIs modernas, sync y async, HTTP/2 |
| aiohttp | Mucha concurrencia async, control fino |
| urllib | Sin dependencias externas, casos muy simples |

### Timeouts recomendados

| Tipo | Valor tipico | Cuando |
|------|--------------|--------|
| connect | 5s | Establecer conexion TCP |
| read | 30s | Esperar datos del servidor |
| write | 30s | Enviar datos al servidor |
| pool | 5s | Esperar conexion del pool |

### ¿Cuando reintentar?

| Codigo | Reintentar? | Razon |
|--------|-------------|-------|
| 200 | No | Exito |
| 400 | No | Peticion mal formada, no se arregla sola |
| 401 | No | Falta autenticacion |
| 404 | No | Recurso no existe |
| 429 | Si | Rate limit, esperar y reintentar |
| 500 | Si | Error del servidor, puede ser transitorio |
| 503 | Si | Servicio no disponible temporalmente |
| Timeout | Si | Puede ser transitorio |

### Ejemplo: cliente httpx basico

    import httpx

    with httpx.Client(timeout=10.0) as client:
        response = client.get("https://rickandmortyapi.com/api/character/1")
        response.raise_for_status()
        data = response.json()
        print(data["name"])

### Ejemplo: streaming a disco

    import httpx
    from pathlib import Path

    with httpx.Client(timeout=30.0) as client:
        with client.stream("GET", "https://ejemplo.com/archivo-big.json") as r:
            r.raise_for_status()
            with Path("big.json").open("wb") as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)

### Ejemplo: reintentos manuales con backoff

    import time
    import httpx

    def get_con_reintentos(url: str, max_attempts: int = 3) -> dict:
        for attempt in range(1, max_attempts + 1):
            try:
                r = httpx.get(url, timeout=10.0)
                r.raise_for_status()
                return r.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if attempt == max_attempts:
                    raise
                delay = 0.5 * (2 ** (attempt - 1))
                print(f"Intento {attempt} fallo: {e}. Reintentando en {delay}s")
                time.sleep(delay)
        raise RuntimeError("unreachable")

### Testing con MockTransport (sin red)

    import httpx

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 1, "name": "Rick"})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        r = client.get("https://test/character/1")
        assert r.json()["name"] == "Rick"

## Checklist
- [x] Crear estructura del laboratorio
- [x] Instalar httpx
- [x] Implementar cliente con timeouts
- [x] Implementar reintentos con backoff
- [x] Implementar paginacion
- [x] Implementar streaming a disco
- [x] Escribir tests con MockTransport
- [x] Correr ruff y mypy
- [x] Documentar en README del laboratorio
- [x] Commit del modulo

## Referencias
- httpx docs: https://www.python-httpx.org/
- httpx — Timeouts: https://www.python-httpx.org/advanced/timeouts/
- httpx — MockTransport: https://www.python-httpx.org/advanced/transports/#mock-transport
- requests docs: https://requests.readthedocs.io/
- aiohttp docs: https://docs.aiohttp.org/
- tenacity docs: https://tenacity.readthedocs.io/
- Rick and Morty API: https://rickandmortyapi.com/documentation
- MDN — HTTP status: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- RFC 9110 — HTTP Semantics: https://www.rfc-editor.org/rfc/rfc9110.html
