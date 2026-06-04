# Panel de Gestion para Salon de Belleza

Aplicacion web full-stack construida con Flask para la gestion de citas de un salon de belleza.
Muestra indicadores clave del dia, graficas interactivas con Chart.js y un formulario para crear
citas, con proteccion CSRF y cabeceras de seguridad.

## Caracteristicas

- Panel con KPIs: citas totales, completadas, tasa de finalizacion e ingresos del dia
- Graficas interactivas: distribucion de estados e ingresos por servicio
- Creacion de citas con validacion en servidor
- API JSON para alimentar las graficas
- Proteccion CSRF en formularios
- Cabeceras de seguridad y politica de contenido (CSP)
- Datos de demostracion precargados

## Arquitectura

```
salon-dashboard/
├── wsgi.py                       Punto de entrada WSGI
├── app/
│   ├── __init__.py               Factoria de la aplicacion y rutas
│   ├── config.py                 Configuracion y ajustes de sesion seguros
│   ├── database.py               Conexion SQLite, esquema y datos demo
│   ├── repository.py             Consultas y agregaciones de KPIs
│   ├── forms.py                  Formularios WTForms con validacion
│   ├── templates/dashboard.html  Plantilla con autoescapado Jinja2
│   └── static/                   CSS y JavaScript del panel
└── tests/                        Suite de pruebas y seguridad
```

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuracion

Variables de entorno relevantes:

```
FLASK_SECRET_KEY=<clave-secreta-larga-y-aleatoria>
FLASK_ENV=production          activa cookies seguras
SALON_DB_PATH=salon.db        ruta de la base de datos
```

## Uso

```bash
python wsgi.py
```

La aplicacion queda disponible en `http://127.0.0.1:5000`. En produccion se recomienda
servirla con un servidor WSGI como gunicorn y tras un proxy inverso con HTTPS.

Rutas principales:

```
GET  /                          Panel principal
POST /appointments              Crear cita
GET  /api/kpis                  KPIs del dia en JSON
GET  /api/status-breakdown      Distribucion de estados
GET  /api/revenue-by-service    Ingresos por servicio
```

## Pruebas

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Seguridad

- Proteccion CSRF en todos los formularios mediante Flask-WTF
- Cookies de sesion con `HttpOnly`, `SameSite=Lax` y `Secure` en produccion
- Autoescapado de Jinja2 que neutraliza intentos de XSS
- Validacion de entrada en servidor con WTForms
- Consultas SQL parametrizadas y restricciones CHECK en la base de datos
- Validacion de parametros de fecha en todas las rutas
- Politica de seguridad de contenido (CSP) restrictiva
- Cabeceras `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`
- Limite de tamano de cuerpo de peticion
- Manejadores de error que devuelven JSON sin exponer trazas
- Analisis estatico con `bandit` sin incidencias
- Auditoria de dependencias con `pip-audit` sin vulnerabilidades conocidas
