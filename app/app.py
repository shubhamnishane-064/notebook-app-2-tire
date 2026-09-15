from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'database'),
    'database': os.environ.get('DB_NAME', 'notebookdb'),
    'user': os.environ.get('DB_USER', 'storeuser'),
    'password': os.environ.get('DB_PASSWORD', 'storepass123'),
    'port': os.environ.get('DB_PORT', '5432')
}


def get_db_connection(max_retries=10):
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except psycopg2.OperationalError as e:
            logger.warning(f"DB connection attempt {i+1} failed: {e}")
            time.sleep(2)
    raise Exception("Could not connect to database after retries")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/notebooks', methods=['GET'])
def get_notebooks():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM notebooks ORDER BY id DESC')
        notebooks = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(notebooks), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/notebooks', methods=['POST'])
def add_notebook():
    try:
        data = request.get_json()

        required = ['title', 'brand', 'price']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            '''INSERT INTO notebooks (title, brand, price, pages, stock,
            description) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *''',
            (
                data['title'],
                data['brand'],
                float(data['price']),
                int(data.get('pages', 100)),
                int(data.get('stock', 0)),
                data.get('description', '')
            )
        )

        notebook = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"Notebook saved: {notebook['title']}")
        return jsonify(notebook), 201

    except Exception as e:
        logger.error(f"Error saving: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/notebooks/<int:notebook_id>', methods=['DELETE'])
def delete_notebook(notebook_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM notebooks WHERE id = %s', (notebook_id,))
        conn.commit()
        deleted = cur.rowcount
        cur.close()
        conn.close()

        if deleted:
            return jsonify({'success': True}), 200
        return jsonify({'error': 'Notebook not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
