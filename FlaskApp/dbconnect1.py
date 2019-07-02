import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

def connection():
	conn =MySQLdb.connect(host="localhost",user ="root",password="vikki",db="Payroll")
	c = conn.cursor()
	return c, conn
