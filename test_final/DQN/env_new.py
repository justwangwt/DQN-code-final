# import gym
# from gym import spaces
import torch
import torch.nn as nn
import torch.optim as optim
import json
import tool
from tool import container_states
# from tool import container_merge
import socket
import time

class CustomEnv():
    def __init__(self):
        super(CustomEnv, self).__init__()
        # 初始化环境参数和状态空间、动作空间等
        #self.observation_space = spaces.Discrete(...)####################
        
        #self.action_space = spaces.Discrete(2)
        # 其他环境参数的初始化

        ## 定义离散动作空间，取值范围为 0 ,1 0 表示拆散,1表示合并
        #self.action_space = list(range(2))
        self.action_space = [0, 1]
        # 定义状态空间为一个包含多个 ContainerState 对象的列表
        #self.state_space = [ContainerState(*container_state) for container_state in container_states]
        # 定义状态空间为【CPU.MEM,等】
        # con = tool.ContainerState("name_1","name_2",20.3)
        # [con.container1_cpu_usage,con.container2_cpu_usage,con.container1_memory_usage,con.container2_memory_usage,con.communication_delay]
        self.state_space = []

        #结果列表
        self.result_dict = {}
        self.reward = 0
    
    #发送消息
    def send_message(self):
        host = '172.19.206.70'
        port = 22
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        try:
            # 连接到目标主机
            sock.connect((host, port))
            print("连接成功")

            # 将字典序列化为 JSON 字符串
            message = json.dumps(self.result_dict)

            # 发送消息
            sock.sendall(message.encode())

        except ConnectionRefusedError:
            print("连接失败，请检查目标主机的 IP 地址和端口号是否正确。")

        finally:
            # 关闭连接
            sock.close()


    
    def reset(self):
        # 重置环境状态并返回初始观测
        # 设置环境的初始状态
        tool.load_data_function()
        # print(self.state_space)
      
        # 返回初始观测

        # 调用数据爬取文件和数据处理文件
        # 获得当前数据信息，初始化状态表##数据里得告诉我当前这两个机器是否合并了呀
       

    
    #返回初始状态
    def get_initial_state(self):
        self.reset()
        for container_name, container_state in container_states.items():
            # 添加容器对象的值到状态空间
            state = [
                container_state.container1_cpu_usage,
                container_state.container2_cpu_usage,
                container_state.container1_memory_usage,
                container_state.container2_memory_usage,
                container_state.communication_delay  # communication_delay
            ]
            self.state_space.append(state)
           # 将状态空间转换为张量
        # print(self.state_space)
        # initial_state = torch.tensor(self.state_space, dtype=torch.float32)
        # 提取数字并转换为浮点数
        self.state_space = [[float(num) if isinstance(num, str) and num.replace(".", "", 1).isdigit() else num for num in sublist] for sublist in self.state_space]
        initial_state = torch.tensor(self.state_space, dtype=torch.float32)

        return initial_state#返回的是容器对列表
    
    #execute_action需要dqn循环调用，给出每一对容器的action
    #
    def execute_action(self,action):
        #action01列表
        # 处理
        action = action.detach().numpy()
        for container_name, container_state in container_states.items():
            #获取并删除action的第一个值
            self.result_dict[container_name] = action.ptp(0)#针对某一个容器对的action结果调用的返回结果

        # self.state_space.remove(state)
        #都调用完成,将结果返回给机器
        # if container_name in container_states and container_states[container_name] == list(container_states.values())[-1]:
        #     done = False#已经遍历到字典最后一个值
        # else:
        #     done = True
        # return done
            #发送消息
            self.send_message()
            time.sleep(5 * 60)
        
            self.reset(self)
            #tool.load_data_function()
            #统计新排版后的reward值
            for container_name, container_state in container_states.items():
                self.reward += container_state.communication_delay

            next_state = self.get_initial_state(self)


            done = True
            return next_state, self.reward , done
        
    
    def render(self):
        # 可选：显示环境的当前状态
        #没有可视化功能
        pass

# 创建自定义环境实例
#env = CustomEnv()





        