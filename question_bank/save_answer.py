import re
import urllib.request
import urllib.parse
import json
import xlrd

from question_bank import hfut


class SaveAnswer(hfut.Hfut):

    # 找到选项对应的列
    @staticmethod
    def get_index(select):
        index = 2
        if select == 'B':
            index = 3
        elif select == 'C':
            index = 4
        elif select == 'D':
            index = 5
        return index

    # 得到答案选项
    @staticmethod
    def get_answer(question_detials, selection):
        if selection == question_detials['optionsA']:
            return 'A'
        elif selection == question_detials['optionsB']:
            return 'B'
        elif selection == question_detials['optionsC']:
            return 'C'
        elif selection == question_detials['optionsD']:
            return 'D'
        return 'A'

    # 从题库获取答案
    @staticmethod
    def get_save_data(path, question_detials, question_json, save_data):
        save_data['examStudentExerciseId'] = question_json['examStudentExerciseId']
        save_data['exerciseId'] = question_json['exerciseId']

        question = question_detials['title'].replace('&nbsp;', '').replace(' ', '')
        options = question_detials['optionsA'].replace('&nbsp;', '').replace(' ', '')
        question_type = question_detials['type']

        workbook = xlrd.open_workbook(path)  # 打开表格
        if question_type == 1:
            sheet = workbook.sheet_by_name("单选题")  # 对应的页
            # 将题目和第一列对比
            for i in range(1, sheet.nrows - 1):
                if question == str(sheet.cell_value(i, 0)).replace(" ", ""):
                    for j in range(2, 5):
                        if options == str(sheet.cell_value(i, j)).replace(" ", ""):
                            index = SaveAnswer.get_index(sheet.cell_value(i, 7))  # 获取选项
                            selection = sheet.cell_value(i, index)  # 获取答案
                            answer = SaveAnswer.get_answer(question_detials, selection)
                            save_data['DXanswer'] = answer
                    save_data['content'] = ''
                    return save_data
        elif question_type == 2:
            if not save_data.get("DXanswer") is None:
                del save_data["DXanswer"]
            sheet = workbook.sheet_by_name("判断题")  # 对应的页
            # 将题目和第一列对比
            for i in range(1, sheet.nrows - 1):
                if question == str(sheet.cell_value(i, 0)).replace(" ", ""):
                    selection = sheet.cell_value(i, 2)  # 获取答案
                    answer = SaveAnswer.get_answer(question_detials, selection)
                    save_data['content'] = ''
                    save_data['PDanswer'] = answer
                    return save_data
        elif question_type == 3:
            pass
        elif question_type == 4:
            pass
        return save_data

    # 保存答案
    @staticmethod
    def save_answer(save_url, save_data, question_json, config):
        if config == '0':
            if question_json['complete'] == 'false':
                save_data = urllib.parse.urlencode(save_data).encode('utf-8')
                req = urllib.request.Request(hfut.Hfut.base_url + save_url, save_data, headers=hfut.Hfut.header)
                result = json.loads(hfut.Hfut.opener.open(req).read().decode('utf-8'))
                print(str(int(question_json['index']) + 1) + ": " + str(result))
        elif config == '1':
            save_data = urllib.parse.urlencode(save_data).encode('utf-8')
            req = urllib.request.Request(hfut.Hfut.base_url + save_url, save_data, headers=hfut.Hfut.header)
            result = json.loads(hfut.Hfut.opener.open(req).read().decode('utf-8'))
            print(str(int(question_json['index']) + 1) + ": " + str(result))

    # 提交答案
    @staticmethod
    def submit_answer(submit_url, is_submit):
        if is_submit == 'y':
            submit_header = hfut.Hfut.header
            submit_header['X-Requested-With'] = 'XMLHttpRequest'  # ajax请求标识
            req = urllib.request.Request(hfut.Hfut.base_url + submit_url, data=None, headers=submit_header)
            result = hfut.Hfut.opener.open(req).read().decode('utf-8')
            print("submit: "+str(result))

    # 选择模式
    @staticmethod
    def set_config():
        number_pattern = re.compile("[01]")  # 检验数字

        print("选择刷题模式")
        print("0: 不覆盖原有答案（默认）")
        print("1: 覆盖原有答案")
        config = input()

        if len(config) == 0:
            return '0'
        elif not len(config) == 1:  # 长度一位
            print("请检查长度")
            return SaveAnswer.set_config()
        elif not len(number_pattern.findall(config)) == 1:  # 0或1
            print("请输入0或1")
            return SaveAnswer.set_config()
        return config

    # 是否提交答案
    @staticmethod
    def is_submit():
        ny_pattern = re.compile("[yn]")  # 检验y或n

        print("选择是否提交答案")
        print("n: 只保存不提交（默认）")
        print("y: 保存并提交")
        config = input()

        if len(config) == 0:
            return 'n'
        elif not len(config) == 1:  # 长度一位
            print("请检查长度")
            return SaveAnswer.is_submit()
        elif not len(ny_pattern.findall(config)) == 1:  # n或y
            print("请输入n或y")
            return SaveAnswer.is_submit()
        return config



