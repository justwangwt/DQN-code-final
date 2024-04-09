import torch
import torch.nn as nn
import torch.optim as optim
import os
import numpy as np 
import random 
import math
from collections import namedtuple, deque
import torch.nn.functional as F
import env_new

GAMMA = 0.9                                     # reward discount
MEMORY_CAPACITY = 2000                          # 记忆库容量
TARGET_REPLACE_ITER = 100                       # 目标网络更新频率
BATCH_SIZE = 32                                 # 样本数量
env = env_new.CustomEnv()
EPSILON = 0.9
##N_ACTIONS = env_new.CustomEnv.action_space      # 动作个数 (2个)
##N_STATES = env_new.CustomEnv.state_space       # 状态个数 ()
LR=0.01
EPISODE=400


Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):
    #经验回放

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class Net(nn.Module):
    def __init__(self):

        super().__init__()
        ##self.fc1=nn.Linear(N_STATES,128)
        ##self.fc1.weight.normal_(0,0.1)
        ##self.fc2=nn.Linear(128,256)
        ##self.fc2.weight.normal_(0,0.1)
        ##self.fc3=nn.Linear(256.512)
        ##self.fc3.weight.normal_(0,0.1)
        ##self.fc4=nn.Linear(512,128)
        ##self.fc4.weight.normal_(0,0.1)
        ##self.fc5=nn.Linear(128,12)
        ##self.fc5.weight.normal_(0,0.1)
        self.conv1=nn.Conv1d(11,32,kernel_size=3)
        self.fc1=nn.Linear(32,64)
        self.fc1.weight.data.normal_(0,0.1)
        self.fc2=nn.Linear(64,11)
        self.fc2.weight.data.normal_(0,0.1)
    
    def forward(self,x):
        ##x=F.relu(self.fc1(obs))
        ##x=F.relu(self.fc2(x))
        ##x=F.relu(self.fc3(x))
        ##x=F.relu(self.fc4(x))
        ##self_out=self.fc5(x)
        x=F.relu(self.conv1(x))
        x=F.max_pool1d(x,2)
        x=x.view(-1,self.num_flat_features(x))
        self_out=F.relu(self.fc1(x))
        self_out=F.relu(self.fc2(self_out))
        ##self_out=torch.sigmoid(self.fc2(x))
        self_out[self_out!=0]=1
        self_out=self_out.view(11,1)
        print(self_out)
        return self_out
    
    def num_flat_features(self,x):
        size=x.size()[1:]
        num_features=1
        for s in size:
            num_features*=s
        return num_features
    

class DQN(object):
    def __init__(self):
        self.main_Network=Net()

        self.target_Network=Net()

        self.learn_step_counter = 0                  # for target updating
        self.memory_counter = 0          # for storing memory
        self.memory = np.zeros((MEMORY_CAPACITY, 4))##########################################
        # self.memory = np.zeros((MEMORY_CAPACITY, env.state_space * 2 + 2), dtype=list)
        self.optimizer=torch.optim.Adam(self.main_Network.parameters(),LR)
        self.criterion=nn.BCELoss()

    def choose_Action(self,x):
        x=torch.unsqueeze(torch.FloatTensor(x),0)
        if np.random.random()<EPSILON:
            print(x)
            action=self.main_Network.forward(x)
        else:
            action=np.random.randint(0,2)
        return action
    
    def store_transition(self,s,a,r,s_):
        transition=np.hstack((s,[a,r],s_))
        index=self.memory_counter%MEMORY_CAPACITY
        self.memory[index,:]=transition
        self.memory_counter+=1
        
    def learn(self):
        N_STATES = env_new.CustomEnv.state_space################################
        # 目标网络参数更新
        if self.learn_step_counter% TARGET_REPLACE_ITER==0:
            self.target_Network.load_state_dict(self.main_Network.state_dict())
            self.learn_step_counter+=1
        
        sample_index=np.random.choice(MEMORY_CAPACITY,self,BATCH_SIZE)
        b_memory = self.memory[sample_index, :]  
        b_s = torch.FloatTensor(b_memory[:, :N_STATES])
        # 将32个s抽出，转为32-bit floating point形式，并存储到b_s中，b_s为32行4列
        b_a = torch.LongTensor(b_memory[:, N_STATES:N_STATES+1].astype(int))
        # 将32个a抽出，转为64-bit integer (signed)形式，并存储到b_a中 (之所以为LongTensor类型，是为了方便后面torch.gather的使用)，b_a为32行1列
        b_r = torch.FloatTensor(b_memory[:, N_STATES+1:N_STATES+2])
        # 将32个r抽出，转为32-bit floating point形式，并存储到b_s中，b_r为32行1列
        b_s_ = torch.FloatTensor(b_memory[:, -N_STATES:])
        # 将32个s_抽出，转为32-bit floating point形式，并存储到b_s中，b_s_为32行4列

        # 获取32个transition的评估值和目标值，并利用损失函数和优化器进行评估网络参数更新
        q_main=self.main_Network(b_s).gather(1,b_a)
        q_next=self.target_Network(b_s).detach()
        q_target=b_r+GAMMA*q_next.max(1)[0].view(BATCH_SIZE,1)
        loss=self.criterion(q_main,q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
# env=env_new.CustomEnv()
#env.get_initial_state()
dqn=DQN()

for i in range(EPISODE):
    print('<<<<<<<<<<Episode:%s'%i)
    s=env.get_initial_state()
    episode_reward_sum=0
    
    while True:
        a=dqn.choose_Action(s)
        s_,r,done=env.execute_action(a)
        
        ## 修改奖励 (不修改也可以，修改奖励只是为了更快地得到训练好的摆杆)
        #x, x_dot, theta, theta_dot = s_
        #r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
        #r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
        #new_r = r1 + r2
        
        dqn.store_transition(s,a,r,s_)
        episode_reward_sum += r
        
        s=s_
        
        if dqn.memory_counter>MEMORY_CAPACITY:
            dqn.learn()
        
        if done:
            print('episode%s---reward_sum: %s' % (i, round(episode_reward_sum, 2)))
            break



