from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import sqlite3
import os
from datetime import datetime

DB_NAME = 'database.db'

IMAGGA_API_KEY = os.environ.get('IMAGGA_API_KEY', '')
IMAGGA_API_SECRET = os.environ.get('IMAGGA_API_SECRET', '')
IMAGGA_ENDPOINT = 'https://api.imagga.com/v2/tags'

if not IMAGGA_API_KEY or not IMAGGA_API_SECRET:
    print("Atención: Credenciales de imagga no estan, no configuradas")
    print("Configurar las variables de entorno IMAGGA_API_KEY e IMAGGA_API_SECRET")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imagen_url TEXT,
            etiquetas TEXT,
            fecha_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/historial')
def historial():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM resultados ORDER BY fecha_analisis DESC')
    resultados = []
    for row in c.fetchall():
        resultados.append({
            'id': row[0],
            'imagen_url': row[1],
            'etiquetas': row[2].split(',') if row[2] else [],
            'fecha_analisis': row[3]
        })
    conn.close()
    return render_template('historial.html', resultados=resultados)

@app.route('/validar_imagen')
def validar_imagen():
    url = request.args.get('url')
    if not url:
        return jsonify({'valid': False, 'error': 'URL no proporcionada'})
    
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('content-type', '')
        if response.status_code == 200 and content_type.startswith('image/'):
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False, 'error': 'URL no válida o no es una imagen'})
    except:
        return jsonify({'valid': False, 'error': 'No se pudo acceder a la URL'})

@app.route('/analizar', methods=['POST'])
def analizar():
    data = request.get_json()
    urls = data.get('urls', [])
    
    if not urls or len(urls) == 0:
        return jsonify({'error': 'No se proporcionaron URLs'}), 400
    
    resultados = []

    for img_url in urls:
        if not img_url.strip():
            continue
            
        try:
            response = requests.get(
                IMAGGA_ENDPOINT,
                params={'image_url': img_url},
                auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                tags = data.get('result', {}).get('tags', [])[:5]
                
                if tags:
                    etiquetas = [f"{tag['tag']['en']} ({tag['confidence']:.1f}%)" for tag in tags]
                    
                    resultados.append({
                        'url': img_url,
                        'etiquetas': etiquetas,
                        'error': None
                    })

                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute(
                        'INSERT INTO resultados (imagen_url, etiquetas) VALUES (?, ?)',
                        (img_url, ','.join([tag['tag']['en'] for tag in tags]))
                    )
                    conn.commit()
                    conn.close()
                else:
                    resultados.append({
                        'url': img_url,
                        'etiquetas': None,
                        'error': 'No se encontraron etiquetas para esta imagen'
                    })
            else:
                resultados.append({
                    'url': img_url,
                    'etiquetas': None,
                    'error': f'Error de API: {response.status_code}'
                })
        except Exception as e:
            resultados.append({
                'url': img_url,
                'etiquetas': None,
                'error': f'Error al procesar: {str(e)}'
            })

    return jsonify({'resultados': resultados})

@app.route('/resultados')
def resultados():
    return render_template('resultado.html')

@app.route('/limpiar_historial', methods=['POST'])
def limpiar_historial():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('DELETE FROM resultados')
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/eliminar_historial/<int:id>', methods=['DELETE'])
def eliminar_historial(id):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('DELETE FROM resultados WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
