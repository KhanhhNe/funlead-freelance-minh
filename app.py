from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def main_route():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        pass


if __name__ == '__main__':
    app.run()
