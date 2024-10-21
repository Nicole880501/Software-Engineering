import os, requests, random, string, hashlib
from flask import Blueprint, redirect, request, render_template
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from campus_eats import UserTable, Customer  # 匯入需要的資料表類別


# 建立實體
customers_blueprints = Blueprint( 'customers', __name__, template_folder= 'templates/customers', static_folder='./static')

customers_blueprints.secret_key = os.urandom(24)  # Session 加密用
# OAuth 設定
CLIENT_ID = '20241007203637hgWIOoOg6QGH'  # 從中央大學 Portal 申請
CLIENT_SECRET = 'YUustASvU0LWPSFXygagued9EILygcfv4h3xofCYJYAuQEoMXrLatvFy'  # 從中央大學 Portal 申請
AUTHORIZATION_URL = 'https://portal.ncu.edu.tw/oauth2/authorization'
TOKEN_URL = 'https://portal.ncu.edu.tw/oauth2/token'
USER_INFO_URL = 'https://portal.ncu.edu.tw/apis/oauth/v1/info'
REDIRECT_URI = 'http://localhost:5000/customers/callback'  # 回調 URL
SCOPE = 'id identifier chinese-name email mobile-phone personal-id'


# 創建資料庫引擎
DATABASE_URL = 'mysql+pymysql://cednjlyzwh:v0USi3Fg$vf8oNoT@se-temp-server.mysql.database.azure.com/campus_eats'
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

# 隨意生成一組12碼密碼
def generate_random_encryped_password(length=12):
    # 定義可以包含的字符：字母、數字和特殊符號
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # 使用 random.choices 從 characters 中隨機選取指定長度的字符
    password = ''.join(random.choices(characters, k=length))
    
    return password

# 加密密碼
def encrypt_password(password):
    # 使用 hashlib 的 sha256 進行加密
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    
    return encrypted_password

# 教職員生 Portal 登入
@customers_blueprints.route('/NCUlogin', methods=['GET','POST'])
def portal():
    return redirect(f'{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}')

# Poratl授權完成後的回調處理
@customers_blueprints.route('/callback')
def callback():
    # 取得授權碼
    code = request.args.get('code')

    if not code:
        return "Authorization code not found.", 400

    # 交換授權碼為 access token
    token_response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }, headers={
        'Accept': 'application/json'
    })

    # 確認 token 回應
    token_json = token_response.json()
    if 'access_token' not in token_json:
        return "Failed to get access token.", 400

    access_token = token_json['access_token']

    # 使用 access token 取得使用者資訊
    user_info_response = requests.get(USER_INFO_URL, headers={
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    })

    # Portal 回傳的資料
    user_info = user_info_response.json()
    # print(user_info)
    
    # user_table/customer - username
    username = user_info.get('identifier')
    # user_table - password
    password = encrypt_password(user_info.get('personalId')[-4:])
    # user_table - role (1.顧客 2.店家)
    role = 1

    # customer - name
    name = user_info.get('chineseName')
    # customer - phone
    phone = user_info.get('mobilePhone')
    # customer - email
    email = user_info.get('email')

    # 建立資料庫連線
    with get_session() as session:
        
        # Step 1. 查詢該學號是否有在用戶資料表中(user_table)
        IsUserExist = session.query(UserTable).filter_by(username=username).first() is not None
        
        # Step 2A. 有在用戶資料表中 -> 登入成功，顯示餐廳清單頁面
        if IsUserExist:
            return render_template('customers/index.html')
        
        # Step 2B. 沒有用戶資料表中 -> 自動新增資料用戶資料表(user_table) + 顧客清單表(customer)
        else:
            
            # Step 3. 資料先寫入user_table(用戶資料表)
            new_user = UserTable(username=username, password=password, role=role)
        
            # 將新物件加入 session
            session.add(new_user)
            print(f"User '{username}' added to UserTable successfully.")

            # Step 4. 資料再寫入customer(顧客清單)
            new_customer = Customer(name=name, phone=phone, email=email, username=username)

            # 將新物件加入 session
            session.add(new_customer)
            print(f"User '{username}' added to Customer successfully.")

            # Step 5. call back (return) 餐廳 list
            return render_template('customers/index.html')

