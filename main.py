from flask import Flask, render_template, request, send_file
import yt_dlp
import os
from urllib.parse import quote

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            ydl_opts = {
                'format': 'best[height<=720]',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            return render_template('result.html', 
                               title=info.get('title', ''),
                               filename=filename)
        except Exception as e:
            return f"خطا: {str(e)}"
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
# from flask import Flask, jsonify
# import os

# app = Flask(__name__)


# @app.route('/')
# def index():
#     return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


# if __name__ == '__main__':
#     app.run(debug=True, port=os.getenv("PORT", default=5000))
