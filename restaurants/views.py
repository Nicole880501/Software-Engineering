import hashlib
import os
from contextlib import contextmanager
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from campus_eats import Restaurant, UserTable, Customer

# 建立實體
restaurants_blueprints = Blueprint('restaurants', __name__, template_folder='templates/restaurants', static_folder='./static')

restaurants_blueprints.secret_key = os.urandom(24)  # Session 加密用

# 創建資料庫引擎
DATABASE_URL = 'mysql+pymysql://root:mysql@localhost/campus_eats'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# 創建一個上下文管理器來自動管理 Session 的生命週期
@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()  # 若有任何變更需要提交
    except Exception as e:
        session.rollback()  # 發生錯誤時回滾事務
        raise
    finally:
        session.close()  # 結束後關閉 session

# 加密密碼
def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 店家登入
@restaurants_blueprints.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_session() as db_session:
            user = db_session.query(UserTable).filter_by(username=username, role=2).first()  # role=2 表示店家
            if user and user.password == encrypt_password(password):
                session['username'] = username
                session['role'] = user.role
                return redirect(url_for('restaurants.management'))  # 導向管理頁面
            else:
                flash('帳號或密碼錯誤！')
                return redirect(url_for('restaurants.login'))  # 重定向回登入頁面

    return render_template('restaurants/login.html')  # 提供登入頁面

# 店家註冊
@restaurants_blueprints.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 獲取註冊表單中的資料
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        restaurant_name = request.form['restaurant_name']
        phone = request.form['phone']
        address = request.form['address']
        business_hours = request.form['business_hours']

        # 基本驗證
        if not all([username, password, confirm_password, restaurant_name, phone, address, business_hours]):
            flash('所有欄位都是必填的！')
            return redirect(url_for('restaurants.register'))

        if password != confirm_password:
            flash('密碼不一致，請重新輸入！')
            return redirect(url_for('restaurants.register'))

        if len(password) < 6:
            flash('密碼至少需要6個字符！')
            return redirect(url_for('restaurants.register'))

        if not phone.isdigit() or len(phone) != 10:
            flash('電話號碼應為10位數字！')
            return redirect(url_for('restaurants.register'))

        # 建立資料庫連線
        with get_session() as db_session:
            # 檢查使用者是否已存在
            is_user_exist = db_session.query(UserTable).filter_by(username=username).first() is not None
            if is_user_exist:
                flash('帳號已存在，請選擇其他帳號')
                return redirect(url_for('restaurants.register'))

            # 儲存新用戶到資料庫
            new_user = UserTable(username=username, password=encrypt_password(password), role=2)  # 角色2表示店家
            new_restaurant = Restaurant(restaurant_name=restaurant_name, phone=phone, address=address, business_hours=business_hours, username=username)

            db_session.add(new_user)
            db_session.add(new_restaurant)
            db_session.commit()

        flash('註冊成功，歡迎！')
        return redirect(url_for('restaurants.management'))  # 註冊成功後導向店家管理頁面

    return render_template('restaurants/register.html')  # 提供註冊頁面

@restaurants_blueprints.route('/management')
def management():
    if 'username' not in session or session.get('role') != 2:
        flash('請先登入！')
        return redirect(url_for('home'))
    return render_template('restaurants/management.html')
