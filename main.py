from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import yt_dlp
import os
from datetime import datetime

app = FastAPI()

@app.get("/download")
async def download_video(url: str):
    try:
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt',
            'quiet': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            def stream_file():
                with open(filename, 'rb') as f:
                    while chunk := f.read(1024*1024):  # 1MB chunks
                        yield chunk
                os.remove(filename)  # حذف فایل پس از ارسال
            
            return StreamingResponse(
                stream_file(),
                media_type='video/mp4',
                headers={
                    'Content-Disposition': f'attachment; filename="{os.path.basename(filename)}"'
                }
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health_check():
    return {"status": "active", "time": datetime.now().isoformat()}