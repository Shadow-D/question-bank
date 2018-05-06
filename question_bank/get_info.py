import re
import urllib.request
import urllib.parse
import zipfile
import json

from question_bank import hfut


class GetInfo:

    # 选择课程
    @staticmethod
    def select_courses(courses):
        number_pattern = re.compile("[0-9]")  # 检验数字
        selection_list = []  # 选择的课程链接
        courses_number = len(courses[0])  # 课程数量
        if courses_number == 0:
            print("没有试题库课程")
            return

        # 输出课程名,选择要完成的课程
        print("\n选择课程，输入格式为 1,2,3 ")
        print("0: 所有课程（默认）")
        for i in range(0, courses_number):
            print(str(i + 1) + ": " + courses[0][i])
        number_input = input()
        input_list = number_input.replace(" ", "").split(",")

        # 判断输入的数据
        for i in input_list:
            if len(i) == 0:
                return courses[1]
            elif not len(i) == 1:  # 长度一位
                print("请检查长度")
                return GetInfo.select_courses()
            elif not len(number_pattern.findall(i)) == 1:  # 数字
                print("请输入数字")
                return GetInfo.select_courses()
            elif int(i) > courses_number:  # 在选项中
                print("请输入正确选项")
                return GetInfo.select_courses()

        # 判断是否选择全部
        for i in input_list:
            if int(i) == 0:
                return courses[1]
            else:
                selection_list.append(courses[1][int(i) - 1])
        return selection_list

    # 下载题库
    @staticmethod
    def get_questions_bank(question_bank_url):
        course_resource_url = hfut.Hfut.base_url + "/filePreviewServlet?indirect=true&resourceId="  # 题库下载链接
        id_pattern = re.compile("\"id\":[0-9]+")  # 题库id
        name_pattern = re.compile("\"fileName\":\".+?\"")  # 文件名称

        # 下载页面
        req = urllib.request.Request(hfut.Hfut.base_url + question_bank_url, headers=hfut.Hfut.header)
        html = hfut.Hfut.opener.open(req).read().decode('utf-8')

        # 获取id和名称
        resource_id = str(id_pattern.search(html).group(0)).split(":")[1]
        zip_name = str(name_pattern.search(html).group(0)).split(":")[1].replace("\"", "")

        # 下载到本地
        req = urllib.request.Request(course_resource_url + resource_id, headers=hfut.Hfut.header)
        download = hfut.Hfut.opener.open(req).read()
        zip_file = open(zip_name, 'wb+')
        zip_file.write(download)

        # 解压
        zip_file = zipfile.ZipFile(zip_name)
        file_name = zip_name.replace(".zip", "")
        zip_file.extract("exercise.xls", file_name)
        file_path = file_name + "/exercise.xls"
        return file_path

    # 题目细节
    @staticmethod
    def get_questions_detials(detials_url, questions_json):
        questions_detials = []

        for i in questions_json:
            target_url = hfut.Hfut.base_url + detials_url + "exerciseId=" + str(i["exerciseId"]) + "&examStudentExerciseId=" + str(i["examStudentExerciseId"])
            detials_header = hfut.Hfut.header
            detials_header['X-Requested-With'] = 'XMLHttpRequest'  # ajax请求标识
            req = urllib.request.Request(target_url, data=None, headers=detials_header)
            question_detials = json.loads(hfut.Hfut.opener.open(req).read().decode('utf-8'))
            questions_detials.append(question_detials)
        return questions_detials

    # 获取课程题库和任务链接
    @staticmethod
    def get_assignments_url(course_url):
        assignment_url_pattern = re.compile("student/teachingTask/taskhomepage\\.do\\?[0-9]{13}&teachingTaskId=[0-9]+")  # 任务页面
        question_bank_url_pattern = re.compile("student/resource/index\\.do\\?[0-9]{13}&&teachingTaskId=[0-9]+&taskId=[0-9]+&history=false")  # 题库页面链接
        exercises_url_pattern = re.compile("student/assignment/manageAssignment\\.do\\?[0-9]{13}&method=doAssignment&assignmentId=[0-9]+&taskId=[0-9]+&history=false")  # 练习页面
        exam_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=doExam&examId=[0-9]+&taskId=[0-9]+&history=false")  # 考试页面

        save_data = {}

        # 进入任务页面
        req = urllib.request.Request(hfut.Hfut.base_url + course_url, headers=hfut.Hfut.header)
        html = hfut.Hfut.opener.open(req).read().decode('utf-8')
        target_url = str(assignment_url_pattern.search(html).group(0))

        save_data['teachingTaskId'] = int(target_url.split("=")[1])

        req = urllib.request.Request(hfut.Hfut.base_url + target_url, headers=hfut.Hfut.header)
        html = hfut.Hfut.opener.open(req).read().decode('utf-8')

        # 题库和任务链接
        question_bank_url = question_bank_url_pattern.search(html).group(0)
        exercises_url = exercises_url_pattern.findall(html)
        exam_url = exam_url_pattern.search(html).group(0)
        return [question_bank_url, exercises_url, exam_url, save_data]

    # 获取任务所有细节
    @staticmethod
    def get_assignment_detials(assignment_url, save_data):
        detials_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=getExerciseInfo&examReplyId=[0-9]+&")  # 题目详情
        save_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=saveAnswer")  # 保存答案
        submit_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=handExam&examReplyId=[0-9]+&examId=[0-9]+&taskStudentId=[0-9]+")
        questions_json_pattern = re.compile("\\[{.+?}.+?{.+?}]")  # 题目信息

        # 做题页面
        req = urllib.request.Request(hfut.Hfut.base_url + assignment_url, headers=hfut.Hfut.header)
        html = hfut.Hfut.opener.open(req).read().decode('utf-8')

        # 题目细节
        questions_json = json.loads(questions_json_pattern.search(html).group(0))
        detials_url = detials_url_pattern.search(html).group(0)
        save_url = save_url_pattern.search(html).group(0)
        questions_detials = GetInfo.get_questions_detials(detials_url, questions_json)
        submit_url = submit_url_pattern.search(html).group(0)

        save_data['examId'] = int(assignment_url.split("=")[2].split("&")[0])
        save_data['examReplyId'] = int(detials_url.split("=")[2].split("&")[0])
        return [save_url, questions_json, questions_detials, submit_url, save_data]


