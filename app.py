import os
import re
import time

from PIL import Image
from flask import Flask, render_template, send_from_directory, request, url_for, redirect

import funlead

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def select_route():
    if request.method == 'GET':
        if not os.path.exists('data.csv') or not os.path.exists('weight.csv'):
            return render_template('select.html')

        time_start_str, time_end_str = 0, 0
        if request.args.get('time_start'):
            time_start_str = request.args['time_start'].removesuffix('00').split()[1]
        if request.args.get('time_end'):
            time_end_str = request.args['time_end'].removesuffix('00').split()[1]

        bit_start = int(request.args.get('bit_start', '0'))
        bit_end = int(request.args.get('bit_end', '15'))

        data_array, _, _, start_time, end_time = funlead.performPCA(
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
        # img_name = 'static/imgs/default_img.png'
        # w, h = (5406, 16)
        # time_start = time_start_str
        # time_end = time_end_str

        return render_template(
            'index.html', img=img_name, img_width=w, img_height=h, pixel_scale=10,
            bit_start=bit_start,
            bit_end=bit_end,
            time_start=time_start,
            time_end=time_end
        )
    else:
        if request.files.get('csv'):
            csv_file = request.files['csv']
            csv_file.save('data.csv')
        if request.files.get('weight'):
            weight_file = request.files['weight']
            weight_file.save('weight.csv')

        if not request.files.get('csv'):
            return redirect(url_for('select_route', **request.args))
        else:
            return redirect(url_for('select_route'))


def parse_time_str(time_str):
    time_info, millis, *_ = re.split(r'\.', time_str) + ['0']
    # Multiply with 100 since time str `00` suffix removed above
    return f"Date.parse('{time_info}').addMilliseconds({int(millis) * 100})"


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
    # Uncomment bellow lines and change port to an open port on machine to deploy on VPS
    # port = 8000
    # app.run('0.0.0.0', port)
