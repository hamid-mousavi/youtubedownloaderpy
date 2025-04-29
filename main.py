from flask import Flask, request, render_template, send_file, after_this_request
import yt_dlp
import tempfile
import os
import threading
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            ydl_opts = {
                'cookiesfrombrowser': ('firefox',),
                'quiet': True,
                'skip_download': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', '')
                formats = []

                for f in info.get('formats', []):
                    if (
                        f.get('vcodec') != 'none' and
                        f.get('acodec') != 'none' and
                        f.get('filesize') and
                        f.get('height')
                    ):
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'height': f['height'],
                            'filesize_mb': round(f['filesize'] / 1024 / 1024, 1)
                        })

                formats = sorted(formats, key=lambda f: f['height'], reverse=True)[:3]

            return render_template('result.html', title=title, formats=formats, url=url)

        except Exception as e:
            return f"خطا: {str(e)}"

    return render_template('index.html')


@app.route('/start_download')
def start_download():
    url = request.args.get('url')
    format_id = request.args.get('format_id')

    try:
        suffix = '.mp3' if format_id == 'mp3' else '.webm'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = temp_file.name
        temp_file.close()

        if format_id == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'ffmpeg_location': 'ffmpeg',
                'cookiesfrombrowser': ('firefox',),
                'quiet': True
            }
        else:
            ydl_opts = {
                'format': format_id,
                'outtmpl': temp_path,
                # 'cookiesfrombrowser': ('firefox',),
                'quiet': True
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # اگر فایل webm بود، به mp4 تبدیلش کن
        if format_id != 'mp3' and temp_path.endswith('.webm'):
            new_path = temp_path.replace('.webm', '.mp4')
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_path,
                '-c:v', 'copy', '-c:a', 'aac', new_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(temp_path)
            temp_path = new_path

        @after_this_request
        def cleanup(response):
            def delayed_delete(path):
                try:
                    os.remove(path)
                    print("✅ فایل حذف شد:", path)
                except Exception as e:
                    print("❌ خطا در حذف فایل:", e)

            threading.Timer(10.0, delayed_delete, args=[temp_path]).start()
            return response

        return send_file(temp_path, as_attachment=True)

    except Exception as e:
        return f"❌ خطا در دانلود: {str(e)}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

    
