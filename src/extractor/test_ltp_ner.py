from ..IOUtil import data_dir

def read_data():
    datas_map = {}
    for filepath in glob.glob(data_dir + '/实体标注/*t*'):
        read_data_from_file(filepath, datas_map)

if __name__ == "__main__":
    