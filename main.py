from flask import Flask, render_template, request, redirect
import csv
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATA_FILE = 'lost_items.csv'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def read_items():
    items = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                items.append(row)
        # 날짜 기준 내림차순 정렬
        items.sort(key=lambda x: x['date'], reverse=True)
    return items

def write_item(item):
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'location', 'date', 'description', 'image', 'category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(item)

@app.route('/')
def index():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    items = read_items()
    if query:
        items = [item for item in items if query.lower() in item['name'].lower()]
    if category:
        items = [item for item in items if item['category'] == category]
    return render_template('index.html', items=items, query=query, category=category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        image_file = request.files['image']
        filename = ''
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
        item = {
            'name': request.form['name'],
            'location': request.form['location'],
            'date': request.form['date'],
            'description': request.form['description'],
            'image': f'/static/uploads/{filename}' if filename else '',
            'category': request.form['category']
        }
        write_item(item)
        return redirect('/')
    return render_template('register.html')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    items = read_items()
    if 0 <= item_id < len(items):
        del items[item_id]
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'location', 'date', 'description', 'image', 'category']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in items:
                writer.writerow(item)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
