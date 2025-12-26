from flask import Flask, request, jsonify, render_template, session
import polars as pl
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'briefmarken-geheim-schluessel-2025')

# Path to the parquet file
PARQUET_FILE = 'stamps.parquet'

# Password for adding stamps (can be set via environment variable)
ADD_STAMP_PASSWORD = os.environ.get('STAMP_PASSWORD', 'briefmarke2025')

# Initialize the parquet file if it doesn't exist
def init_database():
    if not os.path.exists(PARQUET_FILE):
        df = pl.DataFrame(
            schema={
                'database_id': pl.Int64,
                'katalog_id': pl.Utf8,
                'Gebiet': pl.Utf8,
                'jahr': pl.Int64,
                'nennwert': pl.Utf8,
                'beschreibung': pl.Utf8,
                'erhaltung': pl.Utf8,
                'variante': pl.Utf8
            }
        )
        df.write_parquet(PARQUET_FILE)

# Load stamps from parquet file
def load_stamps():
    if os.path.exists(PARQUET_FILE):
        return pl.read_parquet(PARQUET_FILE)
    return pl.DataFrame(
        schema={
            'database_id': pl.Int64,
            'katalog_id': pl.Utf8,
            'Gebiet': pl.Utf8,
            'jahr': pl.Int64,
            'nennwert': pl.Utf8,
            'beschreibung': pl.Utf8,
            'erhaltung': pl.Utf8,
            'variante': pl.Utf8
        }
    )

# Save stamps to parquet file
def save_stamps(df):
    df.write_parquet(PARQUET_FILE)

# Generate a new ID
def get_next_id():
    df = load_stamps()
    if df.is_empty():
        return 1
    return int(df['database_id'].max()) + 1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')

@app.route('/api')
def api_info():
    return jsonify({
        'message': 'Stamp Database API',
        'endpoints': {
            'GET /stamps': 'Get all stamps',
            'GET /stamps/<id>': 'Get a specific stamp',
            'POST /stamps': 'Create a new stamp',
            'PUT /stamps/<id>': 'Update a stamp',
            'DELETE /stamps/<id>': 'Delete a stamp'
        }
    })

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user with password"""
    data = request.get_json()
    
    if 'password' not in data or data['password'] != ADD_STAMP_PASSWORD:
        return jsonify({'error': 'Invalid password'}), 403
    
    session['authenticated'] = True
    return jsonify({'message': 'Login successful'}), 200

@app.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('authenticated', None)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    return jsonify({'authenticated': session.get('authenticated', False)})

@app.route('/stamps', methods=['GET'])
def get_stamps():
    """Get all stamps"""
    df = load_stamps()
    stamps = df.to_dicts()
    return jsonify(stamps)

@app.route('/stamps/<int:stamp_id>', methods=['GET'])
def get_stamp(stamp_id):
    """Get a specific stamp by ID"""
    df = load_stamps()
    stamp = df.filter(pl.col('database_id') == stamp_id)
    
    if stamp.is_empty():
        return jsonify({'error': 'Stamp not found'}), 404
    
    return jsonify(stamp.to_dicts()[0])

@app.route('/stamps', methods=['POST'])
def create_stamp():
    """Create a new stamp"""
    # Check if user is authenticated
    if not session.get('authenticated', False):
        return jsonify({'error': 'Authentication required'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['Gebiet', 'katalog_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Load existing stamps
    df = load_stamps()
    
    # Create new stamp
    new_stamp = {
        'database_id': get_next_id(),
        'katalog_id': data.get('katalog_id', ''),
        'Gebiet': data['Gebiet'],
        'jahr': data['jahr'],
        'nennwert': data['nennwert'],
        'beschreibung': data.get('beschreibung', ''),
        'erhaltung': data.get('erhaltung', ''),
        'variante': data.get('variante', '')
    }
    
    # Add to dataframe and save
    new_df = pl.DataFrame([new_stamp])
    df = pl.concat([df, new_df])
    save_stamps(df)
    
    return jsonify(new_stamp), 201

@app.route('/stamps/<int:stamp_id>', methods=['PUT'])
def update_stamp(stamp_id):
    """Update an existing stamp"""
    data = request.get_json()
    df = load_stamps()
    
    # Check if stamp exists
    if stamp_id not in df['database_id'].to_list():
        return jsonify({'error': 'Stamp not found'}), 404
    
    # Update stamp fields
    for key in ['katalog_id', 'Gebiet', 'jahr', 'nennwert', 'beschreibung', 'erhaltung', 'variante']:
        if key in data:
            df = df.with_columns(
                pl.when(pl.col('database_id') == stamp_id)
                .then(pl.lit(data[key]))
                .otherwise(pl.col(key))
                .alias(key)
            )
    
    save_stamps(df)
    
    updated_stamp = df.filter(pl.col('database_id') == stamp_id).to_dicts()[0]
    return jsonify(updated_stamp)

@app.route('/stamps/<int:stamp_id>', methods=['DELETE'])
def delete_stamp(stamp_id):
    """Delete a stamp"""
    # Check if user is authenticated
    if not session.get('authenticated', False):
        return jsonify({'error': 'Authentication required'}), 403
    
    df = load_stamps()
    
    # Check if stamp exists
    if stamp_id not in df['database_id'].to_list():
        return jsonify({'error': 'Stamp not found'}), 404
    
    # Remove stamp and save
    df = df.filter(pl.col('database_id') != stamp_id)
    save_stamps(df)
    
    return jsonify({'message': 'Stamp deleted successfully'}), 200

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
