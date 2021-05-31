import json
import os
import re
import time

from PIL import Image
from flask import Flask, render_template, send_from_directory, request, url_for, redirect

import funlead

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def select_route():
    try:
        file_data = json.load(open('data.json'))
    except OSError:
        file_data = {}

    if request.method == 'GET':
        if not os.path.exists('data.csv') or not os.path.exists('weight.csv'):
            return render_template('select.html')

        time_start_str, time_end_str = 0, 0
        if request.args.get('time_start'):
            time_start_str = request.args['time_start'].split()[1]
        if request.args.get('time_end'):
            time_end_str = request.args['time_end'].split()[1]

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
        os.makedirs(os.path.dirname(img_name), exist_ok=True)
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
            bit_start=bit_start, bit_end=bit_end,
            time_start=time_start, time_end=time_end,
            csv_name=file_data.get('csv'), weight_name=file_data.get('weight')
        )
    else:
        if request.files.get('csv'):
            csv_file = request.files['csv']
            file_data['csv'] = csv_file.filename
            csv_file.save('data.csv')
            remove_previous_data()

        if request.files.get('weight'):
            weight_file = request.files['weight']
            file_data['weight'] = weight_file.filename
            weight_file.save('weight.csv')
            remove_previous_data()

        json.dump(file_data, open('data.json', 'w'))

        if not request.files.get('csv'):
            return redirect(url_for('select_route', **request.args))
        else:
            return redirect(url_for('select_route'))


@app.route('/reset')
def reset_data():
    if os.path.exists('data.csv'):
        os.remove('data.csv')
    if os.path.exists('weight.csv'):
        os.remove('weight.csv')
    remove_previous_data()
    return redirect(url_for('select_route'))


def remove_previous_data():
    with os.scandir(os.path.join(os.getcwd(), 'static', 'imgs')) as it:
        for entry in it:
            os.remove(entry.path)
    if os.path.exists('data.json'):
        os.remove('data.json')


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
