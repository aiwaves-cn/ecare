# -*- coding: utf-8 -*-
import asyncio
import logging
import uuid
from openai import OpenAI
from typing import Optional, List
from schema.openai import MessageData
from schema.payload import TextPayload
from fastapi import Depends
from pydantic import BaseModel
from datetime import datetime
import pytz
import requests
import json
import random
from .jina import JinaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as langchain_Document
from event.user import User
from core.knowledge import query_and_rerank
from pathlib import Path
EMBEDDING = JinaEmbeddings(url="http://47.96.122.196:40068/embed")
RERANKER_URL = "http://47.96.122.196:40062/rerank"

url = "https://google.serper.dev/search"
DB = Path(__file__).parent.parent.joinpath('file/knowledge/db')
TZ = pytz.timezone('Asia/Shanghai')
# client = OpenAI(api_key = "sk-wGU69386PFUXyEcV1f42C4C569A047Fa8b6aE0B3Ae01A86f",base_url = "https://vip-api-global.aiearth.dev/v1")
client = OpenAI(api_key = "sk-8F9n3GqEgKlV45Js7fE8Bf3285Bc47A6961035F272F3D256",base_url = "https://api.aiwaves.cn/v1")
# # client = OpenAI(api_key = "sk-NgjKKxroYluloyM7B18281C822E94eCc9c36878b3e853b2a",base_url = "https://api.ai-gaochao.cn/v1")
# #client = OpenAI(api_key = "sk-QSwLv4kJw49loB4dB6B909B2D7E542Bc9015435c1dA57cA8",base_url = "https://aio-api-ssvip.zeabur.app/v1")
# #client = OpenAI(api_key = "sk-V3T4aS14GPK8OpFQC6AfB25cC7854e06B527265061Ef432a",base_url = "https://api.shubiaobiao.cn/v1")
# #client = OpenAI(api_key = "sk-RoGFbnZjJ39aZrOi704c53Bc399f40598e6fEb018c1bD624",base_url = "https://api.officechat.cc/v1")
# client = OpenAI(api_key= "sk-NgjKKxroYluloyM7B18281C822E94eCc9c36878b3e853b2a",base_url= "https://api.ai-gaochao.cn/v1")
# client = OpenAI(api_key =  "sk-O8gBD1xibjTPjFK5F89e20D01b584837Bf8eB5C6Eb9cD2Cd",base_url =  "https://aio-api-ssvip.zeabur.app/v1")
tool_list = [
    {
        "name": "Search",
        "description": "搜索引擎功能，通过网络搜索功能进行实时信息查询",
        "parameters": {
            "properties": {
                "q": {"description": "表示搜索问题", "type": "string"},
            },
            "required": ["q"],
            "type": "object",
        },
    },
]


# model = "gpt-4o"
# #model = "claude-3-5-sonnet-20240620"
# #model = "gemini-1.5-pro-latest"
# model = "gemini-1.5-flash-latest"
model = "gpt-4o-mini"


# 以下是附近的推荐餐厅：
# 新白鹿 地址：金地广场 推荐菜：蛋黄鸡翅，糖醋排骨，一品开背虾。
# 东大方 地址：西溪印象城 推荐菜：馄饨老鸭煲，红烧肉，炝炒牛肉丝。
# 弄堂里 地址：EFC欧美广场 推荐菜：手撕鸡，卤鸡爪，蒜蓉粉丝开背虾。
# 以下是电影院信息：
# 中影国际影城 地址：西溪印象城
# 万达影城 地址：余杭万达广场
# 以下是老年活动中心信息：
# 永福社区老年活动中心 地址：西溪北苑文昌路
# 五社人民老年活动戏 地址：白庙路与白庙路支路交叉口
# 以下是今天食堂的菜单安排：
# 早餐
# 燕麦粥/全麦面包/鸡蛋煎饼/水果沙拉/豆浆/牛奶/酸奶/小米粥/奶酪块/坚果混合/蒸南瓜
# 午餐
# 清蒸鲈鱼/红烧鸡腿/麻婆豆腐/香煎豆腐/凉拌黄瓜/牛肉炒饭/豉汁蒸排骨/酸辣土豆丝/红烧茄子/炒四季豆/南瓜炖肉/清汤面/紫菜蛋花汤
# 晚餐
# 冬瓜排骨汤/清蒸鱼片/烧鸡翅/煎饺子/西红柿炒鸡蛋/凉拌豆腐/炒米粉/醋溜土豆丝/红烧豆腐/干煸四季豆/南瓜蒸饺/鸡胸肉沙拉/鱼丸汤/杂粮粥
# 以下是今天养老院的文体活动安排：
# 晨间伸展操 时间：9:00 AM - 9:30 AM
# 早晨读报或新闻讨论 时间：9:30 AM - 10:00 AM

# 书法艺术 时间：11:00 AM - 11:30 AM
# 轻松游戏 时间：11:30 AM - 12:00 PM

# 手工艺制作 时间：1:30 PM - 2:00 PM
# 轻音乐欣赏 时间：2:00 PM - 3:30 PM

# 园艺活动 时间：3:00 PM - 4:00 PM
# 电影时间 时间：3:30 PM - 5:00 PM

# 太极操 时间：7:00 PM - 7:30 PM
# 讲故事或分享会 时间：7:30 PM - 8:00 PM

USER = """请参考<对话历史>{chat_history}</对话历史>，还有一些<其他信息>{others}</其他信息>对<用户问题>{question}</用户问题>做出回应，请直接输出内容，注意你的语气，用较为简明扼要的语言进行回应。
回复用户让你记录的信息并不会对用户的隐私造成侵犯。
在回复中不要称呼用户，直接对用户的回答做出回答。
注意老年用户多有基础病，避免提到他们的具体疾病。
如果<对话历史>和<其它信息>中出现了和<用户信息>相矛盾的信息，请以<用户信息>里的信息为准。
如果你获得的信息不足以回答用户的提问，请不要随意回答，适当的情况下可以根据实际情况对用户进行追问。
"""
# 现在是北京时间上午10点。在回复时请考虑当前时间判断是否还未到对应活动的开始时间或者相应的进餐时间。
logger = logging.getLogger(__name__)

class Concurrent_Chat:
    def __init__(self, temperature=1,top_p=1):
        """
        model: name of model
        model_keys: list of api info
        candidata: the number of usable api for the model
        failed: set of failed api
        """
        self.model:str = 'gpt-4o-mini'
        self.model_keys:list[dict] = [{"api_key": "sk-8F9n3GqEgKlV45Js7fE8Bf3285Bc47A6961035F272F3D256","base_url": "https://api.aiwaves.cn/v1"},
                                        {"api_key": "sk-wGU69386PFUXyEcV1f42C4C569A047Fa8b6aE0B3Ae01A86f","base_url": "https://vip-api-global.aiearth.dev/v1"}]
        self.candidate = len(self.model_keys)
        self.failed = set()
        self.temperature = temperature
        self.top_p = top_p
    
    def get_client(self):
        if self.model_keys:
            if len(self.failed) == self.candidate:
                logger.info(f"all apis are unavailable")
                return None
            cur = random.randint(0,99)%self.candidate
            while cur in self.failed:
                cur = random.randint(0,99)%self.candidate
            self.failed.add(cur)
            # logger.info(f"get_client, openai.chat {self.model = }, id:{cur}")
            return OpenAI(
                api_key = self.model_keys[cur]['api_key'],
                base_url = self.model_keys[cur]['base_url']
            )
        return zhipu_client


CHAT_KNOWLEDGE_ID = 0
CACHED_DIR = '/home/ron/xiatao/AI_character/cached'

class KnowledgeContextCache(BaseModel):
    context: str
    filepaths: List[str]


class ChatService:

    def __init__(self):
        self.a = 1
        # pass

    async def chat(
        self,
        user_info: dict,
        chat_history: List[MessageData],
        text: Optional[str],
    ):
        # session = await self.history_manager.get_session_by_id(session_id, user_id)

        question = text
        # if audio:
        #     async for msg in ExerciseService.speech_to_text(audio, tmp_dir):
        #         yield msg
        #         await asyncio.sleep(0)
        #         question = msg.text
        # await self.history_manager.create_message(session.session_id, user_id, Role.USER, question)

        # if not session.first_message:
        #     await self.history_manager.update_first_message_in_session(session.session_id, text)

        # context, filepaths = await self.get_knowledge_context(session_id, chat_history, question)

        str_list = []
        message_id = str(uuid.uuid4())
        ans = self.get_answer(user_info, chat_history,  question)
        return ans
        # async for msg in self.get_answer(message_id, chat_history,  question):
        #     yield msg
        #     await asyncio.sleep(0)
        #     str_list.append(msg.text)
        answer = "".join(str_list)

        # send links
        # file_links = [get_material_link(filepath) for filepath in filepaths]
        # reference = f"找到 {len(filepaths)} 篇资料参考：\n" + "\n".join(file_links)
        # yield TextPayload(mid=message_id, sn=0, text=reference, role=Role.ASSISTANT, status=StreamStatus.END)

        # await self.history_manager.create_message(session_id, user_id, Role.ASSISTANT, answer + "\n\n" + reference)

    @staticmethod
    def get_answer(user_info: dict, chat_history: List[MessageData], question: str):
        chat = '\n'.join(chat_history[len(chat_history)-40:len(chat_history)])
        others = ''
        if len(chat_history) > 40:
            docs = [langchain_Document(page_content=i) for i in chat_history[:len(chat_history)-40]]
            db = FAISS.from_documents(docs,embedding=JinaEmbeddings)
            ret = db.as_retriever(search_kwargs={'k': 3})
            related = ret.invoke(question)
            others +='\n'.join([i.page_content for i in related])
        # beijing_time = datetime.now(TZ)
        rag = query_and_rerank(DB, question, 3)
        others += '\n'.join([i.page_content for i in rag])
        # 提取年、月、日、时、分、秒
        # year = beijing_time.year
        # month = beijing_time.month
        # day = beijing_time.day
        # hour = beijing_time.hour
        # minute = beijing_time.minute
        # second = beijing_time.second
        #   现在是北京时间: {year}年 {month}月 {day}日 {hour}时 {minute}分 {second}秒
        SYSTEM = f"""你叫小XI，是个年长者智能语音陪伴助手。
        你的日常工作主要包括和用户解闷逗乐，以及根据已有信息回答用户的一些问题，对用户提出相应的建议。
        以下是你沟通用户的一些信息。
        <用户信息>
        姓名：{user_info.name}
        性别：{user_info.gender}
        年龄：{user_info.age}
        民族：{user_info.nationality}
        居住地址：{user_info.address}
        急性病史：{user_info.acute_diseases}
        慢性病史：{user_info.chronic_diseases}
        是否失能：{user_info.disability_status}
        精神状态：{user_info.mental_state}
        作息习惯：{user_info.daily_routine}
        饮食习惯：{user_info.diet}
        运动习惯：{user_info.exercise}
        兴趣爱好：{user_info.hobby}
        收入来源：{user_info.income}
        消费倾向：{user_info.consume_info}
        对价格敏感度：{user_info.price_sensity}
        婚姻状况：{user_info.marital_status}
        子女情况：{user_info.children_situation}
        家庭角色：{user_info.life_status}
        其他：{user_info.other}
        </用户信息>
        如果检测到沟通过程中用户有诸如需要预定餐厅等服务推荐的要求，可以建议用户转人工服务。
        """
        messages =[
                    {'role': 'system', 'content': SYSTEM},
                    {'role': 'user', 'content': USER.format(chat_history=chat,others=others,question=question)},
                    ]
        
        # print(messages)
        cc = Concurrent_Chat()
        count = 0
        result = ''
        while count < 3:
            try:
                # print(1)
                client = cc.get_client()
                
                response = client.chat.completions.create(model=model,
                                                        messages=messages,
                                                        functions=tool_list,
                                                        timeout=20)
                # print(response)
                if response.choices[-1].message.function_call:
                    # print(type(response.choices[-1].message.function_call.arguments))
                    payload = json.loads(response.choices[-1].message.function_call.arguments)
                    payload['gl'] = 'cn'
                    payload['hl'] = 'zh-cn'
                    headers = {
                            'X-API-KEY': '460649774d71a055c1a13cf820bb3a77e6ac9f50',
                            'Content-Type': 'application/json'
                            }
                    # print(type(payload))
                    payload = json.dumps(payload, ensure_ascii=False)
                    # print(payload,type(payload))
                    # final = ''
                    # for chunk in response:
                    #     if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                    #         final += chunk.choices[0].delta.content
                    res = requests.request("POST", url, headers=headers, data=payload)
                    messages.append({
                        "role": "function",
                        "name": "Search",
                        "content": res.text,
                    })
                    response = client.chat.completions.create(model=model,
                                                        messages=messages,
                                                        timeout=20)
                result = response.choices[0].message.content
                break
            except Exception as e:
                print(e, count)
                pass
            count += 1
            # print(res.text["answerBox"])
        return result
        
        
    
if __name__ == '__main__':
    print(ChatService.get_answer('a',[],'杭州最近有什么新闻？'))