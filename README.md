# Asistente de Artículos Científicos

Esta aplicación permite generar artículos científicos basados en una biblioteca de PDFs de referencia, utilizando la API de x.ai.

## Instalación

1. Clona este repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecuta la aplicación:
```bash
streamlit run src/app.py
```

2. Abre tu navegador en `http://localhost:8501`

## Estructura del Proyecto

```
├── src/
│   ├── app.py            # Aplicación principal
│   ├── pdf_processor.py  # Procesamiento de PDFs
│   └── ai_handler.py     # Manejo de la API de IA
├── .env                  # Variables de entorno
├── requirements.txt      # Dependencias
└── README.md            # Documentación
```