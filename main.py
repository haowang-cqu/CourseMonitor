from login import login, headers
from typing import Dict
import requests
import yagmail
import json
import time
import os


def load_config(path: str) -> Dict:
    """读取JSON配置文件
    """
    with open(path, "r") as fp:
        config = json.load(fp)
    return config


def send_email(config: Dict, subject: str, message: str):
    """发送通知邮件
    """
    yag = yagmail.SMTP(
        user={
            config["sendEmail"]: 'Robot'
        },
        password=config["sendEmailPassword"],
        host=config["smtpHost"]
    )
    yag.send(
        to=config["receiveEmail"],
        subject = subject, 
        contents = message
    )


def get_course_list(session: requests.Session) -> list:
    """获取选课网的课程列表
    """
    resp = session.get(
        url="http://my.cqu.edu.cn/api/enrollment/enrollment/course-list",
        params={
            "selectionSource": "主修"
        },
        headers=headers
    )
    if resp.status_code != 200:
        return []
    # 把所有课程类别合并到一个列表
    data = resp.json()["data"]
    course_list = []
    for i in data:
        course_list += i["courseVOList"]
    return course_list


def can_choose(config: Dict, course_list: list) -> list:
    """判断监测的课程是否可以选课
    """
    monitor_courses = set(config["courseCode"])
    can_choose_list = []
    for course in course_list:
        if course["codeR"] in monitor_courses and course["courseEnrollSign"] == None:
            can_choose_list.append(course)
    return can_choose_list


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = load_config(config_path)
    session = login(config["username"], config["password"])
    if session is None:
        print("login error")
        os.exit(-1)
    while True:
        # 获取课程列表
        course_list = get_course_list(session)
        if len(course_list) == 0:
            return
        # 获取指定课程中可以选课的列表
        can_choose_list = can_choose(config, course_list)
        if len(can_choose_list) == 0:
            return
        # 发送邮件
        subject = "课程监测通知"
        message = ""
        for course in can_choose_list:
            message += "{}[{}]有空余名额啦!\n".format(course["name"], course["codeR"])
        send_email(config, subject, message)
        time.sleep(config["interval"])


if __name__ == "__main__":
    main()