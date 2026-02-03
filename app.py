from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
import io
import os
import logging
import datetime
import hashlib
from generate_ics import process_zip_files

# Configure logging for agreement records
logging.basicConfig(level=logging.INFO)
agreement_logger = logging.getLogger('agreement_logger')
handler = logging.FileHandler('agreement_audit.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
agreement_logger.addHandler(handler)
agreement_logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

AGREEMENT_VERSION = "1.0-20240523"  # Version tracking

def anonymize_ip(ip):
    """Anonymize IP address by masking the last octet (IPv4) or last block (IPv6)."""
    if not ip:
        return "unknown"
    if "." in ip:
        parts = ip.split(".")
        return ".".join(parts[:3] + ["xxx"])
    elif ":" in ip:
        parts = ip.split(":")
        return ":".join(parts[:3] + ["xxxx"])
    return "unknown"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check for agreement
    agreed = request.form.get('agreed')
    if agreed != 'true':
        return jsonify({'error': 'You must agree to the Terms of Service and Privacy Policy'}), 403

    # Log agreement
    try:
        ip = request.remote_addr
        # Handle proxy headers if behind reverse proxy
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
            
        anonymized_ip = anonymize_ip(ip)
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        # Log entry: IP_HASH | TIMESTAMP | VERSION | UA_HASH
        agreement_logger.info(f"AGREEMENT_ACCEPTED | IP:{anonymized_ip} | VER:{AGREEMENT_VERSION} | UA:{user_agent[:50]}...")
    except Exception as e:
        print(f"Logging error: {e}") # Non-blocking error

    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part'}), 400
    
    files = request.files.getlist('files[]')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    valid_files = []
    for f in files:
        if f.filename.endswith('.zip'):
            valid_files.append(f)
            
    if not valid_files:
        return jsonify({'error': 'No valid zip files found'}), 400
        
    try:
        # Process files in memory
        ics_content = process_zip_files(valid_files)
        
        # Determine output filename
        output_filename = 'course_schedule.ics'
        
        # Save to a temporary file to serve (or serve from memory)
        # Serving from memory is cleaner
        return send_file(
            io.BytesIO(ics_content),
            mimetype='text/calendar',
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on all interfaces for easier access if needed, or localhost
    app.run(debug=True, port=5001)
