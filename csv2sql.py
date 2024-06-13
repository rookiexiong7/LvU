import pandas as pd
import mysql.connector
from mysql.connector import errorcode

# 读取CSV文件
csv_file = 'data.csv'
df = pd.read_csv(csv_file)
# 将NaN值替换为None
df = df.where(pd.notnull(df), None)
# 连接到MySQL数据库
try:
    cnx = mysql.connector.connect(
        user='root',
        password='12345',
        host='localhost',
        database='lvu'
    )
    cursor = cnx.cursor()

    # 将DataFrame中的每一行数据插入到MySQL表中
    for index, row in df.iterrows():
        sql = """INSERT INTO attractions (城市, 景点名称, 攻略数量, 评论数量, 星级, 排名, 简介, 链接, 图片)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE
                 城市 = VALUES(城市),
                 攻略数量 = VALUES(攻略数量),
                 评论数量 = VALUES(评论数量),
                 星级 = VALUES(星级),
                 排名 = VALUES(排名),
                 简介 = VALUES(简介),
                 链接 = VALUES(链接),
                 图片 = VALUES(图片)"""
        cursor.execute(sql, (
            row['城市'], row['景点名称'], row['攻略数量'], row['评论数量'],
            row['星级'], row['排名'], row['简介'], row['链接'], row['图片']
        ))

    # 提交事务
    cnx.commit()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor.close()
    cnx.close()
