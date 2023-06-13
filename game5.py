from tkinter import *
import tkinter as tk
from pyknp import Juman
import openai
import jaconv

N = 100
word_list = set()
juman = Juman()
last_word = ""
openai_organization = "org-qCYB1pmN2WlH153zrIKq5BDo"
openai_api_key = "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"

def ask_ChatGPT(message):
    openai.organization = openai_organization
    openai.api_key = openai_api_key
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response = completion.choices[0].message.content
    return response

def check_last(word):
    if word == "":
        return False
    result = juman.analysis(word)
    mrph_list = result.mrph_list()
    mrph = mrph_list[-1]
    s = jaconv.kata2hira(mrph.yomi)
    if s[-1] == "ん":
        return False
    return True

def check_hinsi(word):
    result = juman.analysis(word)
    mrph_list = result.mrph_list()
    if not mrph_list:
        return False
    mrph = mrph_list[-1]
    if mrph.hinsi == "名詞":
        return True
    return False

def check_small(character):
    small_list = ["ぁ","ぃ","ぅ","ぇ","ぉ","ゃ","ゅ","ょ","ァ","ィ","ゥ","ェ","ォ","ャ","ュ","ョ"]
    if character in small_list:
        return True
    return False

def change_small(s):
    if s=="ぁ" or s=="ァ":
        return "あ"
    elif s=="ぃ" or s=="ィ":
        return "い"
    elif s=="ぅ" or s=="ゥ":
        return "う"
    elif s=="ぇ" or s=="ェ":
        return "え"
    elif s=="ぉ" or s=="ォ":
        return "お"
    elif s=="ゃ" or s=="ャ":
        return "や"
    elif s=="ゅ" or s=="ュ":
        return "ゆ"
    elif s=="ょ" or s=="ョ":
        return "よ"
    return s

def check_initial(last_word, current_word):
    if last_word == "":
        return True
    if current_word == "":
        return False
    result1 = juman.analysis(current_word)
    mrph_list1 = result1.mrph_list()
    mrph1 = mrph_list1[0]
    result2 = juman.analysis(last_word)
    mrph_list2 = result2.mrph_list()
    mrph2 = mrph_list2[-1]
    m1_new = jaconv.kata2hira(mrph1.yomi)
    m2_new = jaconv.kata2hira(mrph2.yomi)
    if m2_new[-1] == "ー":
        last = m2_new[-2:-1]
        if check_small(last):
            last_new = change_small(last)
            if m1_new[0] != last_new:
                return False
            return True
        if m1_new[0] != last:
            return False
        else:
            return True
    if check_small(m2_new[-1]) == False:
        if m1_new[0] != m2_new[-1]:
            return False
        return True
    if check_small(m2_new[-1]):
        yomi_new = change_small(m2_new[-1])
        if m1_new[0] != yomi_new:
            return False
        return True

def win_or_lose(last_word, current_word):
    if (
        current_word not in word_list
        and check_initial(last_word, current_word)
        and check_last(current_word)
        and check_hinsi(current_word)
    ):
        return True
    else:
        response = ""
        if current_word in word_list:
            response += "既出です\n"
        if not check_initial(last_word, current_word):
            response += "始める文字が違います\n"
        if not check_last(current_word):
            response += "「ん」で終わっています\n"
        if not check_hinsi(current_word):
            response += "名詞ではありません\n"
        messages_text.insert(END, response)
        root.update()
        return False


def win_or_lose_for_chatgpt(last_word, current_word):
    if (
        current_word not in word_list
        and check_initial(last_word, current_word)
        and check_last(current_word)
        and check_hinsi(current_word)
    ):
        return True
    return False

def get_lastletter(current_word):
    result = juman.analysis(current_word)
    mrph_list = result.mrph_list()
    mrph = mrph_list[-1]
    if mrph.yomi[-1] == "ー":
        return mrph.yomi[-2:-1]
    return mrph.yomi[-1]

def ask_question():
    word=entry.get()
    entry.delete(0, tk.END)
    response = f"あなた: {word}"
    messages_text.insert(END, response + "\n")
    root.update()
    last_word=""
    if win_or_lose(last_word, word):
        word_list.add(word)
        last_letter = get_lastletter(word)
        if check_small(last_letter):
            last_letter = change_small(last_letter)
        last_word = word
        current_word = ""
        flag = 0
        while win_or_lose_for_chatgpt(last_word, current_word) == False:
            if flag == 0:
                response = f"「{last_letter}」から始まる単語を探しています..."
                messages_text.insert(END, response + "\n")
                root.update()
            flag += 1
            command = f"{last_letter}から始まる名詞を一つ言ってください。"
            current_word = ask_ChatGPT(command)
        response = "ChatGPT: " + current_word
        messages_text.insert(END, response + "\n")
        root.update()
        if win_or_lose(last_word, current_word) == False:
            response = "Chatgptの負けです"
            messages_text.insert(END, response + "\n")
            root.update()
        word_list.add(current_word)
    else:
        response = "あなたの負けです"
        messages_text.insert(END, response + "\n")
        root.update()

root = Tk()
root.title("しりとりゲーム")
root.geometry("400x500")

messages_frame = Frame(root)
scrollbar = Scrollbar(messages_frame)
messages_text = Text(
    messages_frame,
    height=20,
    width=50,
    yscrollcommand=scrollbar.set,
    wrap="word"
)

scrollbar.pack(side=RIGHT, fill=Y)
messages_text.pack(side=LEFT, fill=BOTH)
messages_frame.pack()

input_frame = Frame(root)
entry = Entry(input_frame)
response = "こんにちは！単語を入力してください。"
messages_text.insert(END, response + "\n")
root.update()
button = Button(input_frame, text="送信", command=ask_question)

entry.pack(side=LEFT)
button.pack(side=LEFT)
input_frame.pack()

root.mainloop()
