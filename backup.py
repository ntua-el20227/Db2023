import os

import ftplib

# Create DATABASE BACKUP

os.system('mysql -u root db2023 > database_backup.sql')
