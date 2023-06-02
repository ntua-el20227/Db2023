import os

import ftplib

# Create DATABASE BACKUP

os.system('mysqldump -u root db2023 > database_backup.sql')
