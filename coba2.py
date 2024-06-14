from connectDB import connectionDB


def getUserData(Email):
    SQL_QUERY = '''
    SELECT Username, Password FROM CLIENT WHERE Email = ?
    '''
    result = connectionDB.execute(SQL_QUERY, (Email)).fetchone()

    dictDataUser = {
        "Username": result[0],
        "Hashed_DB_Password": result[1]
    }

    return dictDataUser


hasil = getUserData("chris@gmail.com")
print(hasil["Username"])
print(hasil["Hashed_DB_Password"])
