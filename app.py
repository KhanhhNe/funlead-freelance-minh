import json
import os
import re
import threading
import time
from traceback import format_exc

from PIL import Image
from flask import Flask, render_template, send_from_directory, request, url_for, redirect

import funlead

app = Flask(__name__)
PIXEL_SCALE = 10


@app.route('/')
def select_route():
    return render_template('select.html')


@app.route('/select')
def main_route():
    if not os.path.exists('data.csv') or not os.path.exists('weight.csv'):
        return redirect(url_for('select_route'))

    try:
        file_data = json.load(open('data.json'))
    except OSError:
        file_data = {}

    if request.args.get('reset'):
        if file_data.get('prev_weight'):
            file_data['weight'] = file_data['prev_weight']
            del file_data['prev_weight']
            if os.path.exists('weight.csv'):
                os.remove('weight.csv')
            os.rename('prev_weight.csv', 'weight.csv')
            json.dump(file_data, open('data.json', 'w+'))

    time_start_str, time_end_str = 0, 0
    if request.args.get('time_start'):
        time_start_str = request.args['time_start'].split()[1]
    if request.args.get('time_end'):
        time_end_str = request.args['time_end'].split()[1]

    bit_start = int(request.args.get('bit_start', '0'))
    bit_end = int(request.args.get('bit_end', '15'))
    moving_average = int(request.args.get('moving_average', '1'))
    img_path = f'static/imgs/{time.time()}.png'
    thread = threading.Thread(target=render_image, args=(
        time_start_str, time_end_str,
        bit_start, bit_end, moving_average,
        img_path
    ))
    thread.start()

    # img_path = 'static/imgs/1625025676.9899454.png'

    return render_template(
        'index.html', img=img_path, pixel_scale=PIXEL_SCALE,
        bit_start=bit_start, bit_end=bit_end,
        moving_average=moving_average,
        img_url=img_path, csv_name=file_data.get('csv'), weight_name=file_data.get('weight')
    )


@app.route('/upload', methods=["POST"])
def upload_files():
    try:
        file_data = json.load(open('data.json'))
    except OSError:
        file_data = {}

    if request.files.get('csv'):
        csv_file = request.files['csv']
        file_data['csv'] = csv_file.filename
        csv_file.save('data.csv')
        remove_previous_data()

    if request.files.get('weight'):
        if os.path.exists('weight.csv'):
            if os.path.exists('prev_weight.csv'):
                os.remove('prev_weight.csv')
            os.rename('weight.csv', 'prev_weight.csv')
            file_data['prev_weight'] = file_data['weight']

        weight_file = request.files['weight']
        file_data['weight'] = weight_file.filename
        weight_file.save('weight.csv')
        remove_previous_data()

    json.dump(file_data, open('data.json', 'w'))
    return ''


@app.route('/get-image')
def get_image():
    img_path = request.args.get('img_url', '')
    if os.path.exists(img_path):
        try:
            img_data = json.load(open('img_data.json'))
            if isinstance(img_data.get(img_path), dict) is False:
                return json.dumps({
                    'success': False,
                    'message': img_data[img_path]
                })

            w, h = Image.open(img_path.lstrip('/')).size
            return json.dumps(dict(
                success=True,
                url=img_path,
                width=w,
                height=h,
                **img_data[img_path]
            ))
        except:
            pass
    return '{}'


@app.route('/reset')
def reset_data():
    remove_previous_data(remove_data_files=True)
    return redirect(url_for('select_route'))


def render_image(time_start_str, time_end_str, bit_start, bit_end, moving_average, img_path):
    try:
        img_data = json.load(open('img_data.json'))
    except FileNotFoundError:
        img_data = {}

    try:
        data_array, time_map, x_labels, x_pos, start_time, end_time, moving_average = funlead.performPCA(
            'data.csv', 'weight.csv',
            start_time=time_start_str, end_time=time_end_str,
            bitstart=bit_start, bitend=bit_end, average=moving_average
        )
        img2 = Image.fromarray(data_array)
        img_data[img_path] = {
            'start': parse_time_str(start_time),
            'end': parse_time_str(end_time),
            'labels': x_labels,
            'labels_pos': x_pos,
            'time_map': time_map
        }
        json.dump(img_data, open('img_data.json', 'w+'))
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        img2.save(img_path)
    except:
        open(img_path, 'w+').write('')
        img_data[img_path] = format_exc()

    json.dump(img_data, open('img_data.json', 'w+'))


def remove_previous_data(remove_data_files=False):
    if os.path.exists('static/imgs'):
        with os.scandir('static/imgs') as it:
            for entry in it:
                os.remove(entry.path)
    if os.path.exists('data.json'):
        os.remove('data.json')
    if remove_data_files:
        if os.path.exists('data.csv'):
            os.remove('data.csv')
        if os.path.exists('weight.csv'):
            os.remove('weight.csv')
        if os.path.exists('prev_weight.csv'):
            os.remove('prev_weight.csv')


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
    remove_previous_data(remove_data_files=True)
    app.run('0.0.0.0', port=5000, debug=True)
