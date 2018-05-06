from question_bank.login import Login
from question_bank.get_info import GetInfo
from question_bank.save_answer import SaveAnswer

courses = Login.login()
selected_courses = GetInfo.select_courses(courses)
# 依次完成每门课
for course in selected_courses:
    config = SaveAnswer.set_config()  # 是否覆盖旧答案
    is_submit = SaveAnswer.is_submit()  # 是否提交答案
    assignments_url = GetInfo.get_assignments_url(course)
    file_path = GetInfo.get_questions_bank(assignments_url[0])
    save_data = assignments_url[3]
    # 每个自测
    for exercise_url in assignments_url[1]:
        assignment_detials = GetInfo.get_assignment_detials(exercise_url, save_data)
        save_url = assignment_detials[0]
        questions_json = assignment_detials[1]
        questions_detials = assignment_detials[2]
        submit_url = assignment_detials[3]
        save_data = assignment_detials[4]
        # 每道题
        for i in range(0, len(questions_json)):
            save_data = SaveAnswer.get_save_data(file_path, questions_detials[i], questions_json[i], save_data)
            SaveAnswer.save_answer(save_url, save_data, questions_json[i], config)
        SaveAnswer.submit_answer(submit_url, is_submit)
        print("是否继续，退出输入q")
        q = input()
        if q == 'q':
            exit(0)








