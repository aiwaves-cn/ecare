from core.chat import ChatService
from event.user import get_user
import redis, json
def main():
    return 1

if __name__ == '__main__':
    # a = ChatService()
    # print(ChatService.get_answer('a',[],'杭州最近有什么新闻'))
    client = redis.StrictRedis(host='localhost', port=6378, password='KY4KLoqGq6er8kTXhsuAcA==',decode_responses=True)
    try:
    # 使用 ping 方法检测连接是否成功
        pong = client.ping()
        if pong:
            print("Successfully connected to Redis!")
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
    except redis.exceptions.AuthenticationError as e:
        print(f"Authentication failed: {e}")
    data = {'user_id': 'xtcg',
    'name': '张一鸣',
    'age': 73,
    'gender': '男',
    'address': '杭州市临平区朝阳西路',
    'nationality': '汉族',
    'chronic_diseases': '高血压、慢性肾炎、类风湿关节炎',
    'acute_diseases': '无',
    'disability_status': '是',
    'mental_state': '正常',
    'daily_routine': '晚上10点入睡 早上6点起床',
    'diet': '蔬菜、低盐、牛肉',
    'exercise': '轻度健身',
    'hobby': '钓鱼、游泳、象棋、养鱼',
    'income': '退休工资 8000-12000元',
    'consume_info': '生活、养生保健',
    'price_sensity': '经济实惠',
    'marital_status': '丧偶',
    'children_situation': '独生子',
    'life_status': '独居',
    'other': '在用药物（同仁堂 菊明降压丸、999感冒灵)',}
    client.set('the_user_info_of_xtcg', json.dumps(data, ensure_ascii=False))