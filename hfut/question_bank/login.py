import re
import time
import urllib.parse
import urllib.request

from question_bank.hfut import Hfut


class Login:

    # 登录
    @staticmethod
    def login():
        url1 = "http://tkkc.hfut.edu.cn/getRandomImage.do?"  # 验证码
        url2 = "http://tkkc.hfut.edu.cn/login.do?"  # 登录
        url3 = "http://203.195.136.80:8080/test/captcha"  # 验证码识别

        pattern1 = re.compile("<input\\stype=\"hidden\"\\sname=\"[a-zA-Z]+\"\\svalue=\"announce\"/>")  # 随机字符串
        pattern2 = re.compile("student/teachingTask/coursehomepage\\.do\\?[0-9]{13}&courseId=[0-9]+\">")  # 课程链接
        pattern3 = re.compile("<font color=\"#333\">[\w\W]+?</font>")  # 课程名称
        gmt = "%a %b %d %Y %H:%M:%S GMT+0800 (CST)"  # 时间格式

        print("\n请依次输入帐号和密码，输入q退出")
        user = input("帐号：")
        if user == 'q':
            exit(0)
        password = input("密码：")

        # 获取post数据中的随机字符串
        req = urllib.request.Request(Hfut.base_url, headers=Hfut.header)
        html = Hfut.opener.open(req).read().decode("utf-8")
        res = str(pattern1.search(html).group(0))
        code = res.split(" ")[2].split("\"")[1]

        # 识别验证码
        req = urllib.request.Request(url1 + time.strftime(gmt), headers=Hfut.header)
        img = Hfut.opener.open(req).read()
        captcha = urllib.request.urlopen(url3, img).read().decode("utf-8")

        # post数据
        post_data = {
            code: "announce",
            "password": password,
            "loginMethod": code + "button",
            "logname": user,
            "randomCode": captcha
        }
        post_data = urllib.parse.urlencode(post_data).encode("utf-8")

        # 登录后的页面源码
        req = urllib.request.Request(url2, post_data, headers=Hfut.header)
        html = Hfut.opener.open(req).read().decode('utf-8')

        # 获取课程链接和名称
        courses_link = pattern2.findall(html)
        courses_name = pattern3.findall(html)
        for i in range(len(courses_link)):
            courses_name[i] = re.sub(re.compile("<[\w\W]+?>"), "", courses_name[i])
            courses_link[i] = courses_link[i].split("\"")[0]

        # 判断是否登录成功
        for key in Hfut.cookie:
            if key.name == "loginedMsg":
                if not len(courses_name) == 0:
                    return [courses_name, courses_link]
                else:
                    print("无试题库课程")
                    exit(0)
        print("登录失败，请重试")
        return Login.login()
