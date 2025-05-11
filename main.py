from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route("/download", methods=["GET"])
def download():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    # ذخیره محتوای کوکی از متغیر محیطی
    cookies_env = os.getenv("COOKIES_DATA")
    cookies_path = "cookies.txt"

    if cookies_env:
        with open(cookies_path, "w", encoding="utf-8") as f:
            f.write(cookies_env)

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'extract_flat': False,
    }

    if cookies_env:
        ydl_opts['cookiefile'] = cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            best = next((f for f in formats[::-1] if f.get('url')), None)

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'formats': formats,
                'best_url': best.get('url') if best else None
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

    
