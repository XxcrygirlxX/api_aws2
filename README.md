# Gestión de Vehículos API

Esta es una API RESTful desarrollada con **FastAPI** y **SQLModel** para la gestión de vehículos y clientes.

## Instalación Local

1. **Clonar el proyecto y entrar en la carpeta:**
   ```bash
   cd Fastapi_BaseDeDatos
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   - Copia el archivo `.env.example` a un nuevo archivo llamado `.env`.
   - Edita el archivo `.env` con tus credenciales de PostgreSQL.
   ```bash
   cp .env.example .env
   ```

## Ejecución de la Aplicación

Para iniciar el servidor de desarrollo con recarga automática, ejecuta:

```bash
python app/main.py
```

O alternativamente usando uvicorn directamente:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`. Puedes acceder a la documentación interactiva (Swagger UI) en `http://localhost:8000/docs`.
