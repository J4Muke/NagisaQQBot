from graia.ariadne.app import Ariadne
from graia.ariadne.entry import config
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Group
from graia.ariadne.entry import MentionMe, GroupMessage, Ariadne, MessageChain, Source, Group, Member, MatchTemplate, Plain, At, MemberPerm, MemberInfo, DetectPrefix
import openai
import re
import configparser

# 创建配置解析器
con = configparser.ConfigParser()

#读取配置文件
con.read('config.ini',encoding='utf-8')


openai.api_key = con.get('OPENAI API','key')
charactor = con.get('BOT','charactor')

app = Ariadne(
    config(
        verify_key="nagisa",  # 填入 http插件的VerifyKey
        account= con.getint('QQ','qq_number'),  # 你的机器人的 qq 号
    ),
)

@app.broadcast.receiver("GroupMessage",decorators=[MentionMe()])
async def group_message_listener(app: Ariadne, group: Group, message: MessageChain):
    txt_tmp = message.include(Plain)
    txt = txt_tmp.display.replace('@Nagisa', '').strip()
    print(txt)

    #使用openai回答问题
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": charactor},
            {"role": "user", "content": txt},
        ]
    )

    print(response)
    reply = response['choices'][0]['message']['content']

    await app.send_message(group, MessageChain([Plain(reply)]))

    # 实际上 MessageChain(...) 有没有 "[]" 都没关系



@app.broadcast.receiver("GroupMessage",decorators=[DetectPrefix('私房报名')])
async def private_room_signup_listener(app: Ariadne, group: Group, member: Member, message: MessageChain):
    sender_nickname = member.name
    sender_qq = member.id

    def detect_number_dot(message_chain: MessageChain) -> str:
        text = str(message_chain)  # 将消息链转换为字符串表示形式
        print(text)
        match = re.search(r'(\d+)点', text)  # 使用正则表达式匹配文本中的第一个数字+点
        if match:
            return match.group(0)  # 返回匹配到的结果
        else:
            return ''

    txt_tmp = message
    txt = detect_number_dot(txt_tmp)
    print(txt)

    #检查是否重复报名
    with open("participants.txt", "r") as file:
        lines = file.readlines()

    # 检测目标字符串是否存在于文件中


    for line in lines:
        if sender_nickname in line:
            await app.send_message(group, MessageChain('你报过名了！别捣乱。'))
            return


    # 将发送者信息写入本地文件
    with open("participants.txt", "a") as file:
        file.write(f"{sender_nickname} {txt}\n")


    #检查报名人数
    file_path = "participants.txt"

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    count = 0  # 行数计数器
    nicknames = []  # 存储昵称的列表

    for line in lines:
        nickname = line.split()[0]  # 提取每行的第一个单词作为昵称
        nicknames.append(nickname)
        count += 1

    output = f"已有{count}人报名，{', '.join(nicknames)}"
    print(output)

    if count < 8:
        count = 8 - count
        count = str(count)
        reply = sender_nickname + '报名成功！一定要按时参加哦～' + '\n' + '就差' + count + '个人了，还有鱿鱿报名吗？'
        await app.send_message(group, MessageChain([Plain(reply)]))
    else:
        count = str(count)
        reply = sender_nickname + '报名成功！一定要按时参加哦～' + '\n' + '已经' + count + '个人了，大家别迟到咯～'
        await app.send_message(group, MessageChain([Plain(reply)]))

    if sender_nickname == 'Asuka':
        reply = '帮你报名了，呜呜呜，一个人玩得开心点哦'
        await app.send_message(group, MessageChain(At(31634483),[Plain(reply)]))


    #reply = sender_nickname + '报名成功！一定要按时参加哦～'
    #await app.send_message(group, MessageChain([Plain(reply)]))


@app.broadcast.receiver("GroupMessage",decorators=[DetectPrefix('私房名单')])
async def private_room_signup_listener(app: Ariadne, group: Group, member: Member, message: MessageChain):
    file_path = "participants.txt"

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    count = 0  # 行数计数器
    nicknames = []  # 存储昵称的列表

    for line in lines:
        nickname = line.split()[0]  # 提取每行的第一个单词作为昵称
        nicknames.append(nickname)
        count += 1

    output = f"已经有{count}个人说要来了，{', '.join(nicknames)}。"
    print(output)
    await app.send_message(group, MessageChain([Plain(output)]))


app.launch_blocking()
