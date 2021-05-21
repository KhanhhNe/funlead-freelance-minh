import os
import re

from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__)


@app.route('/')
def main_route():
    img = [os.path.join('imgs', filename) for filename in os.listdir('imgs') if 'labelled' not in filename][0]
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
