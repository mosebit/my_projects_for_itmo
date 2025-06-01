import csv
import os
import shutil

# def divide_sounds_into_groups(rootdir, res_dir):


# получение имен групп и их индексов
def get_file_names_and_indexes(csv_file: str):
    with open(csv_file, newline='') as csvfile:
        # пропуск первой строки (заголовка)

        next(csvfile)
        spamreader = csv.reader(csvfile, delimiter=',')

        classes_dict = {}
        for raw in spamreader:
            if raw[3] not in classes_dict:
                classes_dict[raw[3]] = raw[2]

        print(list(classes_dict.keys()))


def get_category_by_name(filename: str, path_to_csv: str):
    with open(path_to_csv, newline='') as csvfile:
        # пропуск первой строки (заголовка)
        next(csvfile)

        spamreader = csv.reader(csvfile, delimiter=',')

        classes_dict = {}
        for raw in spamreader:
            if raw[0] == filename:
                return {raw[3]: raw[2]}
        else:
            print("Error: filename not found!")
            return -1


def split_files_to_dirs(raw_dir: str, res_dir: str, csv_file):
    for root, subdirs, files in os.walk(raw_dir):
        for file in files:
            category = get_category_by_name(file, csv_file)
            if category == -1: break

            # создаем директорию, если не существует
            dir_for_file = res_dir + '\\' + list(category.keys())[0] + '\\'
            if not os.path.exists(dir_for_file):
                os.makedirs(dir_for_file)

            src_file = root + '\\' + file
            dst_file = dir_for_file + '\\' + file

            shutil.copyfile(src_file, dst_file)


get_file_names_and_indexes('../esc50.csv')
# split_files_to_dirs(raw_dir=r'C:\Users\Bazzz\Desktop\sova\esc_50_audios',
#                     res_dir=r'C:\Users\Bazzz\Desktop\sova\categorisied',
#                     csv_file='esc50.csv')