from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship, declarative_base

# 先不指定具體資料庫，連接 MySQL 伺服器
# engine = create_engine('mysql+pymysql://root:@localhost')
engine = create_engine('mysql+pymysql://auebtznvfn:Se113423000@ncucampuseats-server.mysql.database.azure.com')

# 創建資料庫
with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS campus_eats DEFAULT CHARACTER SET utf8mb4;"))

Base = declarative_base()

# 用戶資料表
class UserTable(Base):
    __tablename__ = 'user_table'
    
    username = Column(String(50), primary_key=True, comment='用戶帳號，PK')
    password = Column(String(255), nullable=False, comment='用戶密碼')
    role = Column(Integer, nullable=False, comment='用戶角色（1顧客、2店家）')
    
    # 用戶與顧客的一對一或一對多關係，指向 Customer 類
    customer = relationship('Customer', back_populates='user')
    
    # 用戶與店家的一對一或一對多關係，指向 Restaurant 類
    restaurant = relationship('Restaurant', back_populates='user')

# 顧客資料表
class Customer(Base):
    __tablename__ = 'customer'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True, comment='顧客ID，自動遞增，PK')
    name = Column(String(100), nullable=False, comment='顧客姓名')
    phone = Column(String(20), comment='顧客電話號碼')
    email = Column(String(100), comment='顧客電子郵件')
    username = Column(String(50), ForeignKey('user_table.username'), comment='對應用戶帳號（FK）')
    
    # 顧客與用戶的一對一或多對一關係，指向 UserTable 類
    user = relationship('UserTable', back_populates='customer')
    
    # 顧客與訂單的一對多關係，指向 OrderTable 類
    orders = relationship('OrderTable', back_populates='customer')

# 店家資料表
class Restaurant(Base):
    __tablename__ = 'restaurant'
    
    restaurant_id = Column(Integer, primary_key=True, autoincrement=True, comment='店家ID，自動遞增，PK')
    restaurant_name = Column(String(100), nullable=False, comment='店家名稱')
    phone = Column(String(20), comment='店家電話號碼')
    address = Column(String(255), comment='店家地址')
    business_hours = Column(String(100), comment='店家營業時間')
    manager = Column(String(50), comment='店家負責人')
    icon = Column(String(255), comment='店家圖示（URL）')
    username = Column(String(50), ForeignKey('user_table.username'), comment='對應用戶帳號（FK）')

    # 店家與用戶的一對一或多對一關係，指向 UserTable 類
    user = relationship('UserTable', back_populates='restaurant')
    
    # 店家與菜單項目的一對多關係，指向 MenuItem 類
    menu_items = relationship('MenuItem', back_populates='restaurant')

# 餐點資料表
class MenuItem(Base):
    __tablename__ = 'menu_item'
    
    item_id = Column(Integer, primary_key=True, autoincrement=True, comment='餐點ID，自動遞增，PK')
    item_name = Column(String(100), nullable=False, comment='餐點名稱')
    price = Column(DECIMAL(10, 2), nullable=False, comment='餐點價格')
    description = Column(Text, comment='餐點描述')
    status = Column(Integer, comment='餐點狀態（0停售、1販售中）')
    item_image = Column(String(255), comment='餐點圖片URL')
    restaurant_id = Column(Integer, ForeignKey('restaurant.restaurant_id'), comment='所屬店家ID（FK）')

    # 餐點與店家的一對多關係，指向 Restaurant 類
    restaurant = relationship('Restaurant', back_populates='menu_items')
    
    # 餐點與訂單明細的一對多關係，指向 OrderDetail 類
    order_details = relationship('OrderDetail', back_populates='menu_item')

# 訂單資料表
class OrderTable(Base):
    __tablename__ = 'order_table'
    
    order_id = Column(Integer, primary_key=True, autoincrement=True, comment='訂單ID，自動遞增，PK')
    total_amount = Column(DECIMAL(10, 2), nullable=False, comment='訂單總金額')
    order_status = Column(Integer, nullable=False, comment='訂單狀態（如：0下單前(在購物車中)、1待處理、2店家確認、3處理中、4已完成、5已刪除）')
    order_time = Column(DateTime, nullable=False, comment='訂單建立時間')
    payment_method = Column(Integer, comment='付款方式（如：1現金、2信用卡）')
    payment_status = Column(Integer, comment='付款狀態（如：0未付款、1已付款）')
    order_note = Column(Text, comment='訂單備註')
    customer_id = Column(Integer, ForeignKey('customer.customer_id'), comment='對應的顧客ID（FK）')

    # 訂單與顧客的多對一關係，指向 Customer 類
    customer = relationship('Customer', back_populates='orders')
    
    # 訂單與訂單明細的一對多關係，指向 OrderDetail 類
    order_details = relationship('OrderDetail', back_populates='order')

# 訂單明細表
class OrderDetail(Base):
    __tablename__ = 'order_detail'
    
    order_detail_id = Column(Integer, primary_key=True, autoincrement=True, comment='訂單明細ID')
    order_id = Column(Integer, ForeignKey('order_table.order_id'), comment='對應的訂單ID')
    item_id = Column(Integer, ForeignKey('menu_item.item_id'), comment='對應的餐點ID')
    item_note = Column(Text, comment='餐點備註')
    quantity = Column(Integer, nullable=False, comment='購買的餐點數量')

    # 訂單明細與訂單的多對一關係，指向 OrderTable 類
    order = relationship('OrderTable', back_populates='order_details')
    
    # 訂單明細與餐點的多對一關係，指向 MenuItem 類
    menu_item = relationship('MenuItem', back_populates='order_details')

# 創建資料庫引擎（使用你的資料庫資訊）
# engine = create_engine('mysql+pymysql://root:@localhost/campus_eats')
engine = create_engine('mysql+pymysql://auebtznvfn:Se113423000@ncucampuseats-server.mysql.database.azure.com/campus_eats')

# 建立所有表格
Base.metadata.create_all(engine)
