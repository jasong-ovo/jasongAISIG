
def readData(path = 'record.txt'):
    with open(path,'r') as f:
        datas = f.readlines()

    sm0 = []
    mem0 = []
    sm1 = []
    mem1 = []

    for data in datas:
        list_data = data.split(' ')
        list_data_final = [i for i in list_data if i != '']
        if list_data_final[0] == '#':
            continue
        elif list_data_final[0] == '0':
            sm0.append(int(list_data_final[1]))
            mem0.append(int(list_data_final[2]))
        elif list_data_final[0] == '1':
            sm1.append(int(list_data_final[1]))
            mem1.append(int(list_data_final[2]))

    return sm0, mem0, sm1, mem1
