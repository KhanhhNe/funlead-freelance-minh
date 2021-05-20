import os

from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__)


@app.route('/')
def main_route():
    img = [os.path.join('imgs', filename) for filename in os.listdir('imgs') if 'labelled' not in filename][0]
    if request.args.get('time_offset'):
        time_offset_str = request.args['time_offset']
    else:
        time_offset_str = '14:16:04'
    time_end_str = request.args.get('time_end', '')
    hours, minutes, secs = map(int, time_offset_str.split(':'))
    time_offset = sum([hours * 60**2, minutes * 60, secs]) * 1000

    bit_start = int(request.args.get('bit_start', '0'))
    bit_end = int(request.args.get('bit_end', '15'))

    return render_template(
        'index.html', img=img, pixel_scale=10,
        time_offset=time_offset,
        bit_start=bit_start,
        bit_end=bit_end
    )


@app.route('/imgs/<path:filename>')
def get_img(filename):
    return send_from_directory('imgs', filename)


if __name__ == '__main__':
    app.run(debug=True)
