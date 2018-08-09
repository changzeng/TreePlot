# encoding: utf-8

import sys, json, argparse
from flask import Flask
from flask import render_template

# python version check
if sys.version[0] == "2":
	reload(sys)  # Reload is a hack
	sys.setdefaultencoding('UTF8')

# add argument
parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, default="")
parser.add_argument('--title', type=str, default="")
args = parser.parse_args()

# argument check
if len(args.data) == 0:
	raise Exception("No data file specified!!!")

app = Flask(__name__)

@app.route('/')
def index():
    with open(args.data) as fd:
        tree_data = json.load(fd)
    return render_template("index.html", tree_data=tree_data, title=args.title)

if __name__  ==  '__main__':
    app.run(host="127.0.0.1", port=8888, debug=True)
