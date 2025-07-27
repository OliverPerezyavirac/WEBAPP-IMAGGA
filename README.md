# WebApp - Imagga API (SaaS)

Esta aplicación consume el servicio SaaS de Imagga para el análisis de imágenes.
Construida con Flask, SQLite y Tailwind y empaquetada en un solo contenedor Docker.

## Cómo ejecutar

1. Clona este repositorio: git clone https://github.com/OliverPerezyavirac/WEBAPP-IMAGGA

Seguir estos pasos:
    a. cd webapp-imagga
    b. Construye la imagen Docker: docker build -t imagga-app .
    c. Ejecuta la aplicación: docker run -p 5000:5000 imagga-app
    d. Desde Edge u otro navegador: http://localhost:5000


## Requisitos

- Docker instalado
- Cuenta en https://imagga.com para API Key y Secret

## ¿Cómo funciona?

- Aparecen 3 imágenes
- Hacer clic en "Analizar", se consulta el API de Imagga
- Se muestran los tags con mayor confianza de la imagen
- Los datos son guardados de forma local
