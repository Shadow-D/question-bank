import re

from question_bank.login import Login
from question_bank.get_info import GetInfo
from question_bank.save_answer import SaveAnswer


# 选择模式
def set_config():
    number_pattern = re.compile("[01]")  # 检验数字
    ny_pattern = re.compile("[yn]")  # 检验y或n

    print("\n选择刷题模式，输入形为 0n 的两位字符串")
    print("0: 不覆盖原有答案（默认）")
    print("1: 覆盖原有答案")

    print("n: 只保存不提交（默认）")
    print("y: 保存并提交")
    input_config = input()

    if len(input_config) == 0:
        return ['0', 'n']
    elif not len(input_config) == 2:  # 长度两位
        print("\n请检查长度")
        return set_config()
    elif not len(number_pattern.findall(input_config)) == 1 or not len(ny_pattern.findall(input_config)) == 1:  # 一种选项有且只有一个
        print("\n请输入正确选项")
        return set_config()

    config = []
    if ny_pattern.search(input_config[0]) is None:
        config.append(input_config[0])
        config.append(input_config[1])
    else:
        config.append(input_config[1])
        config.append(input_config[0])
    return config


# 选择操作
def select_operation():
    number_pattern = re.compile("[0123]")  # 检验数字

    print("\n选择操作")
    print("0: 都做")
    print("1: 刷题（默认）")
    print("2: 讨论")
    print("3：考试")
    input_operation = input()

    if len(input_operation) == 0:
        return '1'
    elif not len(input_operation) == 1:  # 长度一位
        print("\n请检查长度")
        return select_operation()
    elif not len(number_pattern.findall(input_operation)) == 1:  # 选项
        print("\n请输入正确选项")
        return select_operation()
    return input_operation


# 做题
def assignment_run(assignments_url):
    print("\n-----------------------------------------------")
    print("开始自测\n")

    get_config = set_config()
    config = get_config[0]  # 是否覆盖旧答案
    is_submit = get_config[1]  # 是否提交答案
    file_path = GetInfo.get_questions_bank(assignments_url[0])
    raw_save_data = assignments_url[4]

    length = len(assignments_url[1])  # 自测总个数
    count = 0  # 当前次数

    # 每个自测
    for i in range(0, length):
        count += 1
        exercise_url = assignments_url[1][i]
        print("\n...............................................")
        print("开始第" + str(count) + "个自测\n")
        submit_config = is_submit
        assignment_detials = GetInfo.get_assignment_detials(exercise_url, raw_save_data.copy())

        save_url = assignment_detials[0]
        questions_json = assignment_detials[1]
        questions_detials = assignment_detials[2]
        submit_url = assignment_detials[3]
        base_save_data = assignment_detials[4]

        # 保存每道题
        for j in range(0, len(questions_json)):
            save_data = base_save_data.copy()
            save_config = config
            save_detials = SaveAnswer.get_save_detials(file_path, questions_detials[j], questions_json[j], save_data)
            save_data = save_detials[0]
            answer_flag = save_detials[1]
            if answer_flag is False:
                submit_config = 'n'
                save_config = '2'
            SaveAnswer.save_answer(save_url, save_data, questions_json[j], save_config)

        # 提交答案
        SaveAnswer.submit_answer(submit_url, submit_config)

        # 判断是否最后一个
        if not count == length:
            print("\n是否继续下一个自测，退出输入q")
            inp = input()
            if inp == 'q':
                exit(0)
            else:
                continue


# 讨论
def discuss_run(assignments_url):
    print("\n-----------------------------------------------")
    print("开始讨论\n")
    discuss_url = assignments_url[3]
    discuss_detials = GetInfo.get_discuss_detials(discuss_url)
    for discuss in discuss_detials:
        SaveAnswer.submit_discuss_reply(discuss[0], discuss[1])


# 考试
def exam_run(assignments_url):
    print("\n-----------------------------------------------")
    print("开始考试\n")
    print("暂未开始\n")
    # exam_url = assignments_url[2]
    pass


# 运行程序
def run():
    courses = Login.login()
    selected_courses = GetInfo.select_courses(courses)
    operation = select_operation()

    # 依次完成每门课
    for i in range(0, len(selected_courses[0])):
        name = selected_courses[0][i]
        course = selected_courses[1][i]
        assignments_url = GetInfo.get_assignments_url(course)
        print("\n***********************************************")
        print("课程" + name + "开始\n")

        if operation == '0':
            assignment_run(assignments_url)
            discuss_run(assignments_url)
            exam_run(assignments_url)
        elif operation == '1':
            assignment_run(assignments_url)
        elif operation == '2':
            discuss_run(assignments_url)
        elif operation == '3':
            exam_run(assignments_url)

    print("\n是否选择其他操作，继续输入c")
    inp = input()
    if inp == 'c':
        run_continue(courses)
    else:
        exit(0)


# 重复运行
def run_continue(courses):
    selected_courses = GetInfo.select_courses(courses)
    operation = select_operation()

    # 依次完成每门课
    for i in range(0, len(selected_courses[0])):
        name = selected_courses[0][i]
        course = selected_courses[1][i]
        assignments_url = GetInfo.get_assignments_url(course)
        print("\n***********************************************")
        print("课程" + name + "开始\n")

        if operation == '0':
            assignment_run(assignments_url)
            discuss_run(assignments_url)
            exam_run(assignments_url)
        elif operation == '1':
            assignment_run(assignments_url)
        elif operation == '2':
            discuss_run(assignments_url)
        elif operation == '3':
            exam_run(assignments_url)

    print("\n是否选择其他操作，继续输入c")
    inp = input()
    if inp == 'c':
        run_continue(courses)
    else:
        exit(0)
