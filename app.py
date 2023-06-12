from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS
import ffmpeg
import json
import tempfile
import zipfile
import os
app = Flask(__name__)
CORS(app)

video_settings = {
    "vcodec": 'h264_nvenc',
    "preset": 'fast',
    "rc": 'vbr',
    # "b": '5M',
    "b": '2M',
    "acodec": 'copy',
}
font_settings = "'BorderStyle=3,Fontsize=8,PrimaryColour=&Hffffff&,Alignment=10'"


def chunks(movie, subs, output, eq, segment_time, watermark):
    input_image = ffmpeg.input('gl.png', loop=1).filter(
        'scale', 1080, 1920).filter('setsar', 1, 1)
    input_movie = ffmpeg.input(f'{movie}').filter(
        'scale', -1, 1280)

    overlayed = ffmpeg.filter(
        [input_image, input_movie], 'overlay', '(main_w-overlay_w)/2', 0)

    subtitles = overlayed.filter(
        'subtitles', subs, force_style=font_settings) if subs is not None else overlayed

    final = subtitles.filter('drawtext',
                             box=False, boxborderw=0, fontsize=64, text=watermark, x=0, y=1280)
    output = ffmpeg.output(
        final,
        f'{output}-%d.mp4',
        **video_settings,
        shortest=None,
        f='segment',
        segment_time=segment_time,
        reset_timestamps=1,
        **{"map": "1:1"})

    print(output.get_args())
    ffmpeg.run(output)

@app.route('/')
def root():
    return send_file('index.html')
@app.route('/api', methods=['POST'])
def handle_post_request():
    data = request.form.get('data')
    movie = request.files.get('file')

    data = json.loads(data)
    eq = data['eq']
    segment_time = data['segment_time']
    watermark = data['watermark']
    movie.save(f"./tmp/{movie.filename}")
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = temp_dir.name

    chunks(f"./tmp/{movie.filename}", None,
           f"{temp_dir_path}/output", "default", segment_time, watermark)

    zip_file_path = 'temp.zip'
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        # Add all files in the temporary directory to the zip file
        for root, dirs, files in os.walk(temp_dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(
                    file_path, temp_dir_path))

    print(temp_dir_path)
    response = send_file('temp.zip', as_attachment=True)
    temp_dir.cleanup()
    os.remove('temp.zip')
    return response


if __name__ == '__main__':
    app.run(debug=True)
