import os
import re

from PIL import Image
from flask import Flask, render_template, send_from_directory, request, url_for, redirect

import funlead

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def input_files():
    if request.method == 'GET':
        return render_template('input-files.html')
    else:
        csv_file = request.files['csv']
        csv_file.save('data.csv')
        weight_file = request.files['weight']
        weight_file.save('weight.csv')
        data_array = funlead.performPCA('data.csv', 'weight.csv')[0]
        img2 = Image.fromarray(data_array)
        img2.save(f'imgs/calculated.png')
        return redirect(url_for('select_route'))


@app.route('/select')
def select_route():
    img = 'imgs/calculated.png'
    if request.args.get('time_offset'):
        time_start_str = request.args['time_offset']
    else:
        time_start_str = '14:16:04.000'
    time_end_str = request.args.get('time_end', time_start_str)

    time_start = parse_time_str(time_start_str)
    time_end = parse_time_str(time_end_str)

    bit_start = int(request.args.get('bit_start', '0'))
    bit_end = int(request.args.get('bit_end', '15'))

    return render_template(
        'index.html', img=img, pixel_scale=10,
        bit_start=bit_start,
        bit_end=bit_end,
        time_start=time_start,
        time_end=time_end
    )


def parse_time_str(time_str):
    hours, minutes, secs, millis = map(int, re.split(r':|\.', time_str))
    return sum([hours * 60 ** 2, minutes * 60, secs]) * 1000 + millis


@app.route('/imgs/<path:filename>')
def get_img(filename):
    return send_from_directory('imgs', filename)


if __name__ == '__main__':
    app.run(debug=True)
