from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure uploads folder exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')


# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Upload + Display
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    if file:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

        # Read CSV
        df = pd.read_csv(path)

        # Table preview
        table = df.head(10).to_html()

        # Basic Info
        rows, cols = df.shape
        columns = df.columns.tolist()

        # Missing values
        missing = df.isnull().sum().to_dict()

        # Numeric analysis
        numeric_df = df.select_dtypes(include=np.number)

        stats = {}
        if not numeric_df.empty:
            stats['mean'] = numeric_df.mean().to_dict()
            stats['std'] = numeric_df.std().to_dict()
            stats['max'] = numeric_df.max().to_dict()
            stats['min'] = numeric_df.min().to_dict()

        return render_template('result.html',
                               rows=rows,
                               cols=cols,
                               columns=columns,
                               missing=missing,
                               stats=stats,
                               table=table,
                               filename=file.filename)

    return "No file uploaded"


@app.route('/get_values', methods=['POST'])
def get_values():
    file = request.form['file']
    column = request.form['column']

    path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    df = pd.read_csv(path)

    values = df[column].dropna().unique().tolist()

    return render_template('result.html',
                           columns=df.columns.tolist(),
                           values=values,
                           selected_column=column,
                           filename=file,
                           table=df.head().to_html(),
                           rows=df.shape[0],
                           cols=df.shape[1],
                           missing=df.isnull().sum().to_dict(),
                           stats={})

# Filter Route
@app.route('/filter', methods=['POST'])
def filter_data():
    file = request.form['file']
    column = request.form['column']
    value = request.form['value']

    path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    df = pd.read_csv(path)

    

    limit = int(request.form.get('limit', 10))

    # Basic filter (string match)
    filtered = df[df[column].astype(str) == value].head(limit)
    
    values = df[column].dropna().unique().tolist()

    print("FILTERED ROWS:", len(filtered))
    
    table = df.head(10).to_html()
    filtered_table = filtered.to_html()


    return render_template('result.html',
                           rows=df.shape[0],
                           cols=df.shape[1],
                           columns=df.columns.tolist(),
                           missing=df.isnull().sum().to_dict(),
                           stats={},
                           table=df.head(10).to_html(),
                           filename=file,
                           values=values,
                           selected_column=column,
                           filtered_table=filtered_table)
                           
                    
                           


if __name__ == '__main__':
    app.run(debug=True)