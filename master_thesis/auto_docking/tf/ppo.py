
# Standard libraries
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

# AI libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Flatten, Conv2D, Input
from tensorflow.keras import Model
import tensorflow_probability as tfp







class PPOMemory:
    def __init__(self, batch_size):
        self.states = []
        self.vals = []
        self.actions = []
        self.rewards = []
        self.dones = []

        self.batch_size = batch_size

    def generate_batches(self):
        n_states = len(self.states)
        batch_start = np.arange(0, n_states, self.batch_size)
        indices = np.arange(n_states, dtype=np.int64)
        np.random.shuffle(indices)
        batches = [indices[i:i+self.batch_size] for i in batch_start]

        return np.array(self.states),\
                np.array(self.actions),\
                np.array(self.vals),\
                np.array(self.rewards),\
                np.array(self.dones),\
                batches

    def store_memory(self, state, action, vals, reward, done):
        self.states.append(state)
        self.actions.append(action)
        self.vals.append(vals)
        self.rewards.append(reward)
        self.dones.append(done)

    def clear_memory(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.dones = []
        self.vals = []





class actor_network(Model):
    def __init__(self, input_size, number_of_actions, learning_rate):
        super(actor_network, self).__init__()

        # Shape and size of network
        self.hidden1 = Dense(64, activation='relu', input_shape=(17,))
        self.hidden2 = Dense(64, activation='relu')
        self.output_layer = Dense(number_of_actions, activation='tanh')

        self.optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

    def call(self, x):
        x = self.hidden1(x)
        x = self.hidden2(x)
        return self.output_layer(x)

    def save_model(self):
        self.save('neural_network_models/actor_network_model')






class critic_network(Model):
    def __init__(self, input_size, learning_rate):
        super(critic_network, self).__init__()

        # Shape and size of network
        self.hidden1 = Dense(64, activation='relu', input_shape=(17,))
        self.hidden2 = Dense(64, activation='relu')
        self.output_layer = Dense(1)

        self.optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

    def call(self, x):
        x = self.hidden1(x)
        x = self.hidden2(x)
        return self.output_layer(x)

    def save_model(self):
        self.save('neural_network_models/critic_network_model')

















class Agent:
    def __init__(self, input_size, number_of_actions, gamma=0.99, learning_rate=0.00025, gae_lambda=0.95,
            policy_clip=0.2, batch_size=32, n_epochs=10):

        self.gamma = gamma
        self.policy_clip = policy_clip
        self.n_epochs = n_epochs
        self.gae_lambda = gae_lambda

        self.actor = actor_network(input_size, number_of_actions, learning_rate)
        self.critic = critic_network(input_size, learning_rate)
        self.memory = PPOMemory(batch_size)

    def actor_loss(self, state, action, new_action, critic_value, advantage):

        # Predicts actions and values
        new_action = self.actor(np.reshape(state, (1,17)))
        critic_value = self.critic(np.reshape(state, (1,17)))
        critic_value = tf.squeeze(critic_value) # Removes dimensions of size 1 from tensor

        new_action = tf.cast(new_action, np.float64)

        # Ratio of new vs old action
        r_theta = (new_action/action).numpy()[0]

        # Calculate loss
        L_cpi = (r_theta*advantage)

        # Clip function
        L_clip = np.minimum(L_cpi, np.clip(r_theta, 1-self.policy_clip, 1+self.policy_clip)*advantage)

        actor_loss = tf.convert_to_tensor(-L_clip)

        return actor_loss

    def critic_loss(self, advantage, value, critic_value):

        returns = tf.add(advantage, value)
        critic_value = tf.cast(critic_value, np.float64)
        critic_loss = 0.5*((returns-critic_value)**2)

        return critic_loss

    def choose_action(self, observation):

        # Values to return
        action = 0
        value = 0

        # Reshapes for tf input
        observation = np.reshape(observation, ([1,17]))

        # Predict and calculate value
        action = self.actor(observation)
        value = self.critic(observation)

        # Convert values
        action = action.numpy()
        action = np.array(action.flat)
        value = value.numpy()
        value = float(value)

        return action, value

    def remember(self, state, action, vals, reward, done):
        self.memory.store_memory(state, action, vals, reward, done)

    def learn(self):
        for _ in range(self.n_epochs):
            state_arr, action_arr, vals_arr,\
            reward_arr, dones_arr, batches = \
                    self.memory.generate_batches()

        values = vals_arr
        advantages = np.zeros(len(reward_arr), dtype=np.float32)

        # Calculates advantagess
        for t in range(len(reward_arr)-1):
            discount = 1 # Discount factor
            a_t = 0 # advantages at timestep t
            for k in range(t, len(reward_arr)-1):
                a_t += discount*(reward_arr[k] + self.gamma*values[k+1]*\
                        (1-int(dones_arr[k])) - values[k])
                discount *= self.gamma*self.gae_lambda
            advantages[t] = a_t

        #advantages = T.tensor(advantages).to(self.actor.device)
        #values = T.tensor(values).to(self.actor.device)

        for batch in batches[0]:

            state = tf.convert_to_tensor(state_arr[batch], dtype=np.float64)
            action = tf.convert_to_tensor(action_arr[batch], dtype=np.float64)
            advantage = tf.convert_to_tensor(advantages[batch], dtype=np.float64)
            value = tf.convert_to_tensor(values[batch], dtype=np.float64)

            # Predicts actions and values
            new_action = self.actor(np.reshape(state, ([1,17])))
            critic_value = self.critic(np.reshape(state, ([1,17])))
            critic_value = tf.squeeze(critic_value) # Removes dimensions of size 1 from tensor

            # Calculate loss
            actor_loss = self.actor_loss(state, action, new_action, critic_value, advantage)
            critic_loss = self.critic_loss(advantage, value, critic_value)
            print(actor_loss)
            print(critic_loss)
            #exit()

            exit()

            optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
            optimizer.apply_gradients(zip(gradient1, self.actor.trainable_variables))
            optimizer.apply_gradients(zip(gradient2, self.critic.trainable_variables))



            exit()








        exit()




























if __name__ == '__main__':
    my_model = actor_network(input_size=17, number_of_actions=2, learning_rate=0.00025)

    inputs = np.ones((2, 17))
    print(np.shape(inputs))

    #print(my_model.call(inputs))
    outputs = my_model(inputs)
    print(outputs)

    #my_model.build(input_shape=(1,17))
    my_model.summary()

    my_model.save_model()
    another_model = tf.keras.models.load_model('neural_network_models/actor_network_model')

    #print(my_model.hidden1.input)














