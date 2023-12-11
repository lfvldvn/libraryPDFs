from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

UPLOAD_FOLDER = 'pdfs'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_thumbnail_path(pdf_file):
    return os.path.join('static/thumbnails', f"{os.path.splitext(pdf_file)[0]}.png")

@app.route('/')
def index():
    pdf_files = get_pdf_files()
    generate_thumbnails(pdf_files)
    return render_template('index.html', pdf_files=pdf_files, os=os)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/pdfs/<path:filename>')
def download_file(filename):
    return send_from_directory('pdfs', filename, as_attachment=True)

@app.route('/view/<path:filename>')
def view_pdf(filename):
    return send_from_directory('pdfs', filename)

@app.route('/delete/<path:filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    thumbnail_path = get_thumbnail_path(filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    return redirect(url_for('index'))

def get_pdf_files():
    pdf_directory = 'pdfs'
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    return pdf_files

def generate_thumbnails(pdf_files):
    pdf_directory = 'pdfs'
    thumbnails_directory = 'static/thumbnails'

    if not os.path.exists(thumbnails_directory):
        os.makedirs(thumbnails_directory)

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        thumbnail_path = get_thumbnail_path(pdf_file)

        if not os.path.exists(thumbnail_path):
            images = convert_from_path(pdf_path, first_page=0, last_page=1)
            if images:
                images[0].save(thumbnail_path, 'PNG')

if __name__ == '__main__':
    app.run(debug=True)
