from flask import Flask, render_template, Response, request, redirect, url_for, Blueprint
import subprocess
import os
import time
from datetime import datetime

from customers.views import customers_blueprints
from restaurants.views import restaurants_blueprints
import campus_eats

app = Flask(__name__, static_folder='static')

app.register_blueprint(customers_blueprints, url_prefix='/customers')
app.register_blueprint(restaurants_blueprints, url_prefix='/restaurants')

# 登入頁面
@app.route('/')
def index():
    return render_template('index.html')

# 訪客/店家頁面
@app.route('/register')
def register():
    return 0

if __name__ == '__main__':
    app.run(debug=True)


