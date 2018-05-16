import re
import urllib.request
import urllib.parse
import zipfile
import json

from question_bank.hfut import Hfut


class GetInfo:

    # 下载题库
    @staticmethod
    def get_questions_bank(question_bank_url):
        course_resource_url = Hfut.base_url + "/filePreviewServlet?indirect=true&resourceId="  # 题库下载链接
        id_pattern = re.compile("\"id\":[0-9]+")  # 题库id
        name_pattern = re.compile("\"fileName\":\".+?\"")  # 文件名称

        # 下载页面
        req = urllib.request.Request(Hfut.base_url + question_bank_url, headers=Hfut.header)
        html = Hfut.opener.open(req).read().decode('utf-8')

        # 获取id和名称
        resource_id = str(id_pattern.search(html).group(0)).split(":")[1]
        zip_name = str(name_pattern.search(html).group(0)).split(":")[1].replace("\"", "")

        # 下载到本地
        req = urllib.request.Request(course_resource_url + resource_id, headers=Hfut.header)
        download = Hfut.opener.open(req).read()
        zip_file = open("question_bank/file/" + zip_name, 'wb+')
        zip_file.write(download)

        # 解压
        zip_file = zipfile.ZipFile("question_bank/file/" + zip_name)
        file_parent_path = "question_bank/file/" + zip_name.replace(".zip", "")
        zip_file.extract("exercise.xls", file_parent_path)
        file_path = file_parent_path + "/exercise.xls"
        return file_path

    # 题目细节
    @staticmethod
    def get_questions_detials(detials_url, questions_json):
        questions_detials = []

        for i in questions_json:
            target_url = Hfut.base_url + detials_url + "exerciseId=" + str(i["exerciseId"]) + "&examStudentExerciseId=" + str(i["examStudentExerciseId"])
            detials_header = Hfut.header
            detials_header['X-Requested-With'] = 'XMLHttpRequest'  # ajax请求标识
            req = urllib.request.Request(target_url, data=None, headers=detials_header)
            question_detials = json.loads(Hfut.opener.open(req).read().decode('utf-8'))
            questions_detials.append(question_detials)
        return questions_detials

    # 获取课程题库和任务链接
    @staticmethod
    def get_assignments_url(course_url):
        assignment_url_pattern = re.compile("student/teachingTask/taskhomepage\\.do\\?[0-9]{13}&teachingTaskId=[0-9]+")  # 任务页面
        question_bank_url_pattern = re.compile("student/resource/index\\.do\\?[0-9]{13}&&teachingTaskId=[0-9]+&taskId=[0-9]+&history=false")  # 题库页面链接
        exercises_url_pattern = re.compile("student/assignment/manageAssignment\\.do\\?[0-9]{13}&method=doAssignment&assignmentId=[0-9]+&taskId=[0-9]+&history=false")  # 练习页面
        exam_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=doExam&examId=[0-9]+&taskId=[0-9]+&history=false")  # 考试页面
        discuss_url_pattern = re.compile("student/bbs/index\\.do\\?[0-9]{13}&teachingTaskId=[0-9]+")  # 讨论页面

        # 保存答案参数
        save_data = {}

        # 进入任务页面
        req = urllib.request.Request(Hfut.base_url + course_url, headers=Hfut.header)
        html = Hfut.opener.open(req).read().decode('utf-8')
        target_url = assignment_url_pattern.search(html).group(0)
        discuss_url = discuss_url_pattern.search(html).group(0)

        save_data['teachingTaskId'] = int(target_url.split("=")[1])

        req = urllib.request.Request(Hfut.base_url + target_url, headers=Hfut.header)
        html = Hfut.opener.open(req).read().decode('utf-8')

        # 题库和任务链接
        question_bank_url = question_bank_url_pattern.search(html).group(0)
        exercises_url = exercises_url_pattern.findall(html)
        if not exam_url_pattern.search(html) is None:
            exam_url = exam_url_pattern.search(html).group(0)
        else:
            exam_url = None
        return [question_bank_url, exercises_url, exam_url, discuss_url, save_data]

    # 获取任务所有细节
    @staticmethod
    def get_assignment_detials(assignment_url, save_data):
        detials_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=getExerciseInfo&examReplyId=[0-9]+&")  # 题目详情
        save_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=saveAnswer")  # 保存答案
        submit_url_pattern = re.compile("student/exam/manageExam\\.do\\?[0-9]{13}&method=handExam&examReplyId=[0-9]+&examId=[0-9]+&taskStudentId=[0-9]+")
        questions_json_pattern = re.compile("\\[{.+?}.+?{.+?}]")  # 题目信息

        # 做题页面
        req = urllib.request.Request(Hfut.base_url + assignment_url, headers=Hfut.header)
        html = Hfut.opener.open(req).read().decode('utf-8')

        # 题目细节
        questions_json = json.loads(questions_json_pattern.search(html).group(0))
        detials_url = detials_url_pattern.search(html).group(0)
        save_url = save_url_pattern.search(html).group(0)
        questions_detials = GetInfo.get_questions_detials(detials_url, questions_json)
        submit_url = submit_url_pattern.search(html).group(0)

        save_data['examId'] = int(assignment_url.split("=")[2].split("&")[0])
        save_data['examReplyId'] = int(detials_url.split("=")[2].split("&")[0])
        return [save_url, questions_json, questions_detials, submit_url, save_data]

    # 获取两个话题信息
    @staticmethod
    def get_discuss_detials(discuss_url):
        topic_url_pattern = re.compile("student/bbs/manageDiscuss\\.do\\?[0-9]{13}&method=view&teachingTaskId=[0-9]+&discussId=[0-9]+&isModerator=false&isClick=true&forumId=[0-9]+")
        reply_pattern = re.compile("<td\\swidth=\"100%\">[\w\W]+?</td>")
        reply_input_pattern = re.compile("id=\"form1\">\\s+?(<input\\stype=\"hidden\"\\sname=\"[a-zA-Z]+?\"\\svalue=\"[a-zA-Z0-9]+?\"\\s/>\\s+?){5}")
        reply_url_pattern = re.compile("student/bbs/manageDiscuss\\.do\\?[0-9]{13}&method=reply")
        discuss_detials = []

        # 话题页面
        req = urllib.request.Request(Hfut.base_url + discuss_url, headers=Hfut.header)
        html = Hfut.opener.open(req).read().decode('utf-8')
        all_topics_url = topic_url_pattern.findall(html)

        # 获取两条有回复的话题
        topics_length = len(all_topics_url)
        reply_count = 0
        for i in range(0, topics_length):
            req = urllib.request.Request(Hfut.base_url + all_topics_url[i], headers=Hfut.header)
            html = Hfut.opener.open(req).read().decode('utf-8')
            if not reply_pattern.search(html) is None:
                # 两次后停止
                if reply_count == 2:
                    break
                reply_data = {}
                reply = re.sub("<[\s\S]+?>|\s", "", reply_pattern.search(html).group(0))
                # 答案为空时继续下一个话题
                if reply == '':
                    continue
                reply_input = reply_input_pattern.search(html).group(0)
                reply_input = list(filter(None, re.sub("\s|[<>/]+|input|type=\"hidden\"|id=\"form1\"|value=|name=\"[a-zA-Z]+?\"", "", reply_input).split("\"")))
                reply_url = reply_url_pattern.search(html).group(0)

                # 提交讨论参数
                reply_data['discussId'] = reply_input[0]
                reply_data['forumId'] = reply_input[1]
                reply_data['type'] = reply_input[2]
                reply_data['isModerator'] = reply_input[3]
                reply_data['teachingTaskId'] = reply_input[4]
                reply_data['content'] = reply

                discuss_detials.append([reply_url, reply_data])
                reply_count += 1
        return discuss_detials
