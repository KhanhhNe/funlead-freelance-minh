import os
from datetime import time

from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)


@app.route('/')
def main_route():
    if request.method == 'GET':
        imgs = [os.path.join('imgs', filename) for filename in os.listdir('imgs') if 'labelled' not in filename]
        time_offset = sum([14 * 60**2, 16 * 60, 4]) * 1000

        return render_template('index.html', imgs=imgs[:1], time_offset=time_offset, pixel_scale=10)
    else:
        pass


@app.route('/imgs/<path:filename>')
def get_img(filename):
    return send_from_directory('imgs', filename)


if __name__ == '__main__':
    app.run(debug=True)
