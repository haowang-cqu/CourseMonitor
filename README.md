## 选课状态监测

### 功能说明
该程序的目的是帮助同学及时捡课，它可以监测选课网中指定课程的状态，如果这些课程有剩余名额则立即发送邮件通知。
![example](./img/example.png)

### 基本使用
1. 配置Python环境
   ```bash
   python -m venv .venv            # 创建一个虚拟环境
   source .venv/bin/activate       # 激活虚拟环境
   pip install -r requirements.txt # 安装依赖
   ```
2. 编辑配置文件`config.json`，完善基本信息
3. 使用crontab运行定时任务：`crontab -e`然后按需添加定时任务，例如
   ```bash
    */15 * * * * source /opt/CourseMonitor/.venv/bin/activate && python3 /opt/CourseMonitor/main.py >/dev/null 2>&1
   ```
   上述定时任务每15分钟执行一次
4. 用完后删除crontab

### 配置文件
config.json为配置文件模板
```json
{
    "username": "xxxxxx",           // 统一身份认证号或学号
    "password": "xxxxxx",           // 教务网登录密码
    "courseCode": [                 // 想要监测的课程号
        "IPC18004",
        "IPC18003",
        "IPC18002"
    ],
    "sendEmail": "aaaa@qq.com",     // 发送通知的邮箱,以qq邮箱为例
    "sendEmailPassword": "xxxxxxxx",// 发送通知的邮箱密码(登录授权码) 
    "smtpHost": "smtp.qq.com",      // SMTP服务器地址，以qq邮箱为例
    "receiveEmail": "bbbb@bbbb.bbb" // 接收通知的邮箱
}
```
