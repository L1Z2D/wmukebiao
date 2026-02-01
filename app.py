from flask import Flask, render_template, request, send_file, jsonify
import io
import os
from generate_ics import process_zip_files

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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
