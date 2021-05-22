import re
import time
from datetime import timedelta

from dateutil import parser

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

        return redirect(url_for('select_route'))


@app.route('/select')
def select_route():
    time_start_str, time_end_str = 0, 0
    if request.args.get('time_start'):
        time_start_str = request.args['time_start']
    if request.args.get('time_end'):
        time_end_str = request.args['time_end']

    if time_start_str:
        time_start_str = parser.parse(time_start_str).strftime('%Y-%m-%d %H:%M:%S')
        time_end_obj = parser.parse(time_end_str)
        if time_end_obj.microsecond:
            time_end_obj += timedelta(seconds=1)
        time_end_str = time_end_obj.strftime('%Y-%m-%d %H:%M:%S')

    bit_start = int(request.args.get('bit_start', '0'))
    bit_end = int(request.args.get('bit_end', '15'))

    data_array, start_time, end_time = funlead.performPCA(
        'data.csv', 'weight.csv',
        start_time=time_start_str, end_time=time_end_str,
        bitstart=bit_start, bitend=bit_end
    )
    print(start_time, end_time)
    img2 = Image.fromarray(data_array)
    img_name = f'static/imgs/{time.time()}.png'
    img2.save(img_name)

    time_start = parse_time_str(start_time)
    time_end = parse_time_str(end_time)

    w, h = Image.open(img_name.lstrip('/')).size

    return render_template(
        'index.html', img=img_name, img_width=w, img_height=h, pixel_scale=10,
        bit_start=bit_start,
        bit_end=bit_end,
        time_start=time_start,
        time_end=time_end
    )


def parse_time_str(time_str):
    time_info, millis = re.split(r'\.', time_str) + ['0']
    return f"Date.parse('{time_info}').addMilliseconds({millis})"


@app.route('/static/<path:pathname>')
def get_asset(pathname):
    return send_from_directory('static', pathname)


@app.after_request
def disable_caching(response):
    response.cache_control.no_store = True
    response.cache_control.max_age = 0
    return response


if __name__ == '__main__':
    app.run(debug=True)
