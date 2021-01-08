#! /bin/python
# @author: petrus.munteanu, 2020
# due to lack of time, the script is not at all optimized. Repetitions and small mistakes are bound to be found, but feel free to improve the script as you find fit

import os, fnmatch, datetime
from shutil import copy

search_dir = "c:\\workspace\\python\\manage_files\\"
dest_dir = "c:\\workspace\\python\\manage_files\\move_folder"
# search_dir = "c:\\users\\public\\workspace\\pycharm\\test_files\\"
# dest_dir = "c:\\users\\public\\workspace\\pycharm\\test_files\\move_folder\\"

# search_dir = "/home/ctm_user/devops/mongo/dumps/prd/test/test_files/"
# dest_dir = "c:\\users\\public\\workspace\\pycharm\\test_files\\move_folder/"

# how many months the script will process
# The script will ignore the last 2 months - excluding # the current one
# so if you put in 6 months, the script will process 4 months -> from 6 months ago until 2 months ago:
months_search_period = 6
months_keep_period = 2  #how many months of backups to keep in the temporary directory - where the backup is originally stored


''' extract the months which will be processed '''
def find_months():
    month_list = []
    today = datetime.date.today()
    beautiful_day = today.replace(day=10)  # the tenth day of the current month
    for i in range(months_search_period, months_keep_period, -1):
        date = beautiful_day - datetime.timedelta(days=30 * i)
        month_list.append(str(date.strftime("%Y_%m")))
    return month_list
month_list = find_months()


''' search for 6 files of every month except the last 2 months. 6 files reprezent a good backup '''
backup_candidates = []
# looking for files
def search_files(iter_mon):
    iter_backup_candidates = []
    print("looking for files for the " + iter_mon + " month")
    for y in range(1, 29):  # we search each day
        for file in os.listdir(search_dir):
            if len(iter_backup_candidates) != 6:
                if fnmatch.fnmatch(file, str(iter_mon) + "_" + str(y).zfill(2) + "*"):
                    iter_backup_candidates.append(file)
            elif not iter_backup_candidates:
                print("nothing")
            else:
                for item in iter_backup_candidates:
                    backup_candidates.append(item)
                return (backup_candidates)
        iter_backup_candidates = []
for iter_mon in month_list:
    search_files(iter_mon)

print('the following files are elligible for copying to the permanent backup')
for k in backup_candidates:
    print(k)
print

#creating a list with the files full path
absolute_path_files = []
for k in backup_candidates:
    absolute_path_files.append(search_dir + str(k))


''' copy the candidate files in the permanent backup folder '''
if backup_candidates:
    user_input = raw_input("copy them to the permanent backup location? Y/N: ")
    if (user_input.lower() == "yes" or user_input.lower() == "y"):
        for file in absolute_path_files:
            copy(file, dest_dir)
        print("backup files have been copied")
        print
    else:
        print("see you later")
        quit()


''' delete the older files except the last months '''
user_input = raw_input("delete older files? Y/N: ")
if (user_input.lower() == "yes" or user_input.lower() == "y"):
    for i in month_list:
        for rootDir, subdirs, filenames in os.walk(search_dir):
            # Find the files that matches the given patterm
            for filename in fnmatch.filter(filenames, i + '*.gz'):
                try:
                    print("I\'m gonna delete " + filename)
                    os.remove(os.path.join(rootDir, filename))
                except OSError:
                    print("Error while deleting file")
else:
    print("see you later")
    quit()

print("job finished")
