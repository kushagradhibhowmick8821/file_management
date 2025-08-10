from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename
from datetime import datetime  # Import datetime module

app = Flask(__name__)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = '/home/kb/mysite/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'jpg', 'png', 'gif' , 'zip'}  # Set of allowed file extensions

# Define a password for deletion (change this to your desired password)
deletion_password = "admin"

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # List all uploaded files
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/uploads', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        filename = secure_filename(file.filename)
        filename_with_timestamp = f"{timestamp}/{filename}"  # Append timestamp to filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_with_timestamp))
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete_file():
    if request.method == 'POST':
        # Check if the entered password matches the deletion password
        entered_password = request.form.get('password')
        if entered_password == deletion_password:
            filename = request.form.get('filename')

            if filename:
                try:
                    # Ensure the filename is safe (prevent directory traversal)
                    safe_filename = os.path.basename(filename)

                    # Construct the full path to the uploaded files directory
                    upload_folder = app.config['UPLOAD_FOLDER']

                    # Construct the full path to the file
                    file_path = os.path.join(upload_folder, safe_filename)

                    # Check if the file exists and delete it
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        return redirect(url_for('index'))  # Redirect back to the main page after deletion

                except Exception as e:
                    # Handle any errors (e.g., file not found)
                    return str(e)

        # Redirect back to the main page if the password is incorrect
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
