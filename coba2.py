from connectDB import connectionDB


def checkIsEmailExist(Email):
    SQL_QUERY = '''
    SELECT Email FROM Client WHERE Email = ?
    '''

    result = connectionDB.execute(SQL_QUERY, (Email)).fetchone()

    if (result != None):
        # kalau email nya udah kepake
        return True
    else:
        # kalau email nya belum kepake orang lain
        return False


hasil = checkIsEmailExist("ch@gmail.com")
print(hasil)
