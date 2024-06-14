import pyodbc

# data koneksi sql server
SERVER = 'LAPTOP-ES7ENIHT\SQLEXPRESS'
DATABASE = 'tubesJarkom2'
USERNAME = 'sa'
PASSWORD = 'Christian0811'

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Trusted_Connection=yes;TrustServerCertificate=yes;'

# buat koneksi ke sql server
connectionDB = pyodbc.connect(connectionString)
