import os
import ftplib

def restore():
    os.system('mysql -u root db2023 < database_backup.sql')


def backup():
    os.system('mysqldump -u root db2023 > database_backup.sql')