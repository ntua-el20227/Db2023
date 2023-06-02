import os
# Create DATABASE RESTORE

os.system('mysql -u root db2023 < database_backup.sql')
