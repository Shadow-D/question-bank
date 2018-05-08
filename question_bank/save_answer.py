import urllib.request
import urllib.parse
import json
import xlrd

from question_bank import hfut


class SaveAnswer(hfut.Hfut):

    # 找到选项对应的列
    @staticmethod
    def get_index(selection):
        index = 2
        if selection == 'B':
            index = 3
        elif selection == 'C':
            index = 4
        elif selection == 'D':
            index = 5
        # elif selection == 'E':  # 暂未碰到，不确定
        #     index = 6
        return index

    # 得到答案选项
    @staticmethod
    def get_answer(question_detials, answer_value):
        if answer_value == question_detials['optionsA']:
            return 'A'
        elif answer_value == question_detials['optionsB']:
            return 'B'
        elif answer_value == question_detials['optionsC']:
            return 'C'
        elif answer_value == question_detials['optionsD']:
            return 'D'
        # elif answer_value == question_detials['optionsE']:
        #     return 'E'
        return ''

    # 根据答案设置多选题的post数据
    @staticmethod
    def set_save_data(answer, save_data):
        if answer == 'A':
            save_data['DuoXanswerA'] = 'true'
        elif answer == 'B':
            save_data['DuoXanswerB'] = 'true'
        elif answer == 'C':
            save_data['DuoXanswerC'] = 'true'
        elif answer == 'D':
            save_data['DuoXanswerD'] = 'true'
        # elif selection == 'E':
        #     save_data['DuoXanswerE'] = 'true'
        return save_data

    # 从题库获取答案
    @staticmethod
    def get_save_detials(path, question_detials, question_json, save_data):
        answer_flag = False  # 判断是否找到答案

        save_data['examStudentExerciseId'] = question_json['examStudentExerciseId']
        save_data['exerciseId'] = question_json['exerciseId']
        save_data['content'] = ''

        question = question_detials['title'].replace('&nbsp;', '').replace(' ', '')
        options = question_detials['optionsA'].replace('&nbsp;', '').replace(' ', '')
        question_type = question_detials['type']

        workbook = xlrd.open_workbook(path)  # 打开表格

        # 单选题
        if question_type == 1:
            sheet = workbook.sheet_by_name("单选题")  # 对应的页
            # 将题目和第一列对比
            for i in range(1, sheet.nrows - 1):
                if question == str(sheet.cell_value(i, 0)).replace(" ", ""):
                    for j in range(2, 5):
                        if options == str(sheet.cell_value(i, j)).replace(" ", ""):
                            index = SaveAnswer.get_index(sheet.cell_value(i, 7))  # 获取选项
                            answer_value = sheet.cell_value(i, index)  # 获取答案
                            answer = SaveAnswer.get_answer(question_detials, answer_value)
                            save_data['DXanswer'] = answer
                            if not answer == '':
                                answer_flag = True
            return [save_data, answer_flag]
        #  判断题
        elif question_type == 2:
            sheet = workbook.sheet_by_name("判断题")  # 对应的页
            # 将题目和第一列对比
            for i in range(1, sheet.nrows - 1):
                if question == str(sheet.cell_value(i, 0)).replace(" ", ""):
                    answer_value = sheet.cell_value(i, 2)  # 获取答案
                    answer = SaveAnswer.get_answer(question_detials, answer_value)
                    save_data['PDanswer'] = answer
                    if not answer == '':
                        answer_flag = True
            return [save_data, answer_flag]
        # 多选题
        elif question_type == 4:
            sheet = workbook.sheet_by_name("多选题")  # 对应的页
            # 将题目和第一列对比
            for i in range(1, sheet.nrows - 1):
                if question == str(sheet.cell_value(i, 0)).replace(" ", ""):
                    for j in range(2, 5):
                        if options == str(sheet.cell_value(i, j)).replace(" ", ""):
                            selections = sheet.cell_value(i, 7).split(",")
                            print(selections)
                            for selection in selections:
                                index = SaveAnswer.get_index(selection)
                                answer_value = sheet.cell_value(i, index)  # 获取答案
                                answer = SaveAnswer.get_answer(question_detials, answer_value)
                                save_data = SaveAnswer.set_save_data(answer, save_data)
                                if not answer == '':
                                    answer_flag = True
            return [save_data, answer_flag]
        return [save_data, answer_flag]

    # 保存答案
    @staticmethod
    def save_answer(save_url, save_data, question_json, config):
        if config == '0':
            if question_json['complete'] is False:
                save_data = urllib.parse.urlencode(save_data).encode('utf-8')
                req = urllib.request.Request(hfut.Hfut.base_url + save_url, save_data, headers=hfut.Hfut.header)
                result = json.loads(hfut.Hfut.opener.open(req).read().decode('utf-8'))
                print(str(int(question_json['index']) + 1) + ": " + str(result))
        elif config == '1':
            save_data = urllib.parse.urlencode(save_data).encode('utf-8')
            req = urllib.request.Request(hfut.Hfut.base_url + save_url, save_data, headers=hfut.Hfut.header)
            result = json.loads(hfut.Hfut.opener.open(req).read().decode('utf-8'))
            print(str(int(question_json['index']) + 1) + ": "+result['status'])
        elif config == '2':
            print(str(int(question_json['index']) + 1) + ": 未找到答案，请自行查找")

    # 提交题目答案
    @staticmethod
    def submit_answer(submit_url, is_submit):
        if is_submit == 'y':
            submit_header = hfut.Hfut.header
            submit_header['X-Requested-With'] = 'XMLHttpRequest'  # ajax请求标识
            req = urllib.request.Request(hfut.Hfut.base_url + submit_url, data=None, headers=submit_header)
            result = json.loads(hfut.Hfut.opener.open(req).read().decode('utf-8'))
            print("submit: "+result['status'])

    # 提交讨论答案
    @ staticmethod
    def submit_discuss_reply(reply_url, reply_data):
        reply_data = urllib.parse.urlencode(reply_data).encode('utf-8')
        req = urllib.request.Request(hfut.Hfut.base_url + reply_url, data=reply_data, headers=hfut.Hfut.header)
        result = hfut.Hfut.opener.open(req)
        if result.status == 200:
            print("discuss: ok")
