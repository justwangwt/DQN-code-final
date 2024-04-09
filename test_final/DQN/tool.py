#g工具类
import json
import get_and_pro_data_

container_states = {}#改用字典
# container_merge = {}#记录是否合并的数据结构
def load_data_function():
        get_and_pro_data_.get_pro_data()
    #####################
        #进行初始数据读取
        # 读取 JSON 文件
        with open('myenv/durtion.json') as f:
            data = json.load(f)

        

        # 遍历 jaeger JSON 数据并创建 ContainerState 对象
        for key, value in data.items():
            container_names = key.strip('()').split(',')
            container1_name = container_names[0].strip()
            container2_name = container_names[1].strip()
            communication_delay = int(value)
            
            container_state = ContainerState(container1_name, container2_name, communication_delay)
            #container_states.append(container_state)
            container_states[key] = container_state

        #读取所在机器数据
        with open('myenv/data/node_data.json') as f:
            json_data = f.read()
        data = json.loads(json_data)
        containers = {}
        # 创建 Container 对象并添加到字典中
        for container_name, node in data.items():
            container = Container(container_name, node)
            containers[container_name] = container
            

        #其他数据 cpu
        with open('myenv/data/cpu.json') as f:
            json_data = f.read()
        data = json.loads(json_data)
        for container_name, cpu in data.items():
            containers[container_name].set_container_cpu_usage(cpu)
            # print("container_name")
            # print(container_name)
            
        
        with open('myenv/data/mem.json') as f:
            json_data = f.read()
        data = json.loads(json_data)
        for container_name, memory in data.items():
            containers[container_name].set_container_memory_usage(memory)

        with open('myenv/data/net_receive.json') as f:
            json_data = f.read()
        data = json.loads(json_data)
        for container_name, net_receive in data.items():
            containers[container_name].set_container_net_receive(net_receive)

        with open('myenv/data/net_transmit.json') as f:
            json_data = f.read()
        data = json.loads(json_data)
        for container_name, net_transmit in data.items():
            containers[container_name].set_container_net_transmit(net_transmit)

        ################################################################
        # for key in containers:
        #     print(containers[key].container_cpu_usage)

        #给ContainerState赋值
        # 遍历 container_states 列表
        for key in container_states:
            container_state = container_states[key]
            # 获取 container1_name 和 container2_name
            container1_name = container_state.container1_name
           
            container2_name = container_state.container2_name
            
            # 查询 Container 字典获取对应的 Container 对象
            container1 = containers.get(container1_name)
            # print("container1_name")
            # print(container1_name)
            container2 = containers.get(container2_name)

            
            # 将 Container 对象的属性值赋给 ContainerState 对象
            if container1:
                # print("********************************")
                # print(container1.container_name)
                # print(container1.container_cpu_usage)
                container_state.update_container1_stats(container1.container_cpu_usage,
                                                         container1.container_memory_usage,
                                                         container1.container_net_receive,
                                                         container1.container_net_transmit,
                                                         )
                # container_state.container1_cpu_usage = container1.container_cpu_usage
                # container_state.container1_net_receive = container1.container_net_receive
                # container_state.container1_memory_usage = container1.container_memory_usage
                # container_state.container1_net_transmit = container1.container_net_transmit          
            
            if container2:
                # print("***********")
                # print(container2.container_name)
                # print(container2.container_cpu_usage)
                container_state.update_container2_stats(container2.container_cpu_usage,
                                                         container2.container_memory_usage,
                                                         container2.container_net_receive,
                                                         container2.container_net_transmit,
                                                         )
                # container_state.container2_cpu_usage = container1.container_cpu_usage
                # container_state.container2_net_receive = container1.container_net_receive
                # container_state.container2_memory_usage = container1.container_memory_usage
                # container_state.container2_net_transmit = container1.container_net_transmit
            if container1 and container2:
                if container1.node == container2.node:
                    container_state.is_merged = True
        # print("container_state***********")
        # for key in container_states:
        #     container_state = container_states[key]
        #     print("@@@@@@@container_state@@@@")
        #     print(container_state.container1_name)
        #     print(container_state.container1_cpu_usage)
        #     print("@@@@@@@@@@@")
        #     print(container_state.container2_name)
        #     print(container_state.container2_cpu_usage)
              




#创建一个自定义的类，
#类里面存储两个微服务，以及微服务间对应的通信量
#
class ContainerState:
    def __init__(self, container1_name, container2_name,communication_delay):
        self.container1_name = container1_name
        self.container2_name = container2_name
        self.is_merged = False#是否合并
        self.communication_delay = communication_delay
        self.container1_cpu_usage = 0
        self.container1_memory_usage = 0
        self.container1_net_receive = 0
        self.container1_net_transmit = 0
        self.container2_cpu_usage = 0
        self.container2_memory_usage = 0
        self.container2_net_receive = 0
        self.container2_net_transmit = 0
    
    def merge_containers(self):
        self.is_merged = True
    
    def separate_containers(self):
        self.is_merged = False
    
    def update_container1_stats(self, cpu_usage, memory_usage, net_receive, net_transmit):
        self.container1_cpu_usage = cpu_usage
        self.container1_memory_usage = memory_usage
        self.container1_net_receive = net_receive
        self.container1_net_transmit = net_transmit
    
    def update_container2_stats(self, cpu_usage, memory_usage, net_receive, net_transmit):
        self.container2_cpu_usage = cpu_usage
        self.container2_memory_usage = memory_usage
        self.container2_net_receive = net_receive
        self.container2_net_transmit = net_transmit

    def change_merged(self,action):
        if action == 0:
            self.is_merged = False
        else:
            self.is_merged = True


class Container:
    def __init__(self, container_name, node):
        self.container_name = container_name  
        self.container_cpu_usage = 0
        self.container_memory_usage = 0
        self.container_net_receive = 0
        self.container_net_transmit = 0
        self.node = node
    
    def set_node(self, node):
        self.node = node

    def set_container_cpu_usage(self, cpu_usage):
        self.container_cpu_usage = cpu_usage

    def set_container_memory_usage(self, memory_usage):
        self.container_memory_usage = memory_usage

    def set_container_net_receive(self, net_receive):
        self.container_net_receive = net_receive

    def set_container_net_transmit(self, net_transmit):
        self.container_net_transmit = net_transmit
    
    def get_container_cpu_usage(self):
        return self.container_cpu_usage

    
if __name__ == "__main__":
    load_data_function()