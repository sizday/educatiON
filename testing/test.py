def open_file(answer_file, test_file):
    answer_text = str(answer_file, 'utf-8')
    test_text = str(test_file, 'utf-8')
    answer = file_to_list(answer_text)
    test = file_to_list(test_text)
    return compare_answer(answer, test)


def file_to_list(text):
    lists = text.split('\n')
    if lists[-1] == '':
        lists.pop()
    return lists


def compare_answer(answer_list, test_list):
    count = 0
    for i in range(len(answer_list)):
        if answer_list[i] == test_list[i]:
            count += 1
    mark = round(count/len(answer_list)*100) // 20
    return mark


