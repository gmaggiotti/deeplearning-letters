import numpy as np
import tensorflow as tf

num_epochs = 100
total_series_length = 50000
truncated_backprop_length = 15
state_size = 4
num_classes = 2
echo_step = 3
batch_size = 5
num_layers = 3
num_batches = total_series_length//batch_size//truncated_backprop_length

def generateData():
    x = np.array(np.random.choice(2, total_series_length, p=[0.5, 0.5]))
    y = np.roll(x, echo_step)
    y[0:echo_step] = 0
    x = x.reshape((batch_size, -1))  # The first index changing slowest, subseries as rows
    y = y.reshape((batch_size, -1))
    return (x, y)

### tf data structure
batchX_placeholder = tf.placeholder(tf.float32, [batch_size, truncated_backprop_length])
batchY_placeholder = tf.placeholder(tf.int32, [batch_size, truncated_backprop_length])

init_state = tf.placeholder(tf.float32, [num_layers, 2, batch_size, state_size])

state_per_layer_list = tf.unstack(init_state, axis=0)

rnn_tuple_state = tuple(
    [tf.nn.rnn_cell.LSTMStateTuple(state_per_layer_list[idx][0], state_per_layer_list[idx][1])
     for idx in range(num_layers)]
)

W2 = tf.Variable(np.random.rand(state_size, num_classes),dtype=tf.float32)
b2 = tf.Variable(np.zeros((1,num_classes)), dtype=tf.float32)


# Forward passes
cell = [tf.nn.rnn_cell.LSTMCell(state_size, state_is_tuple=True) for i in range(num_layers)]
cell = tf.nn.rnn_cell.MultiRNNCell(cell, state_is_tuple=True)
cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=0.5)
states_series, current_state = tf.nn.dynamic_rnn(cell, tf.expand_dims(batchX_placeholder, -1), initial_state=rnn_tuple_state)
states_series = tf.reshape(states_series, [-1, state_size])

#Calculating loss
logits = tf.matmul(states_series, W2) + b2 #Broadcasted addition
labels = tf.reshape(batchY_placeholder, [-1])

logits_series = tf.unstack(tf.reshape(logits, [batch_size, truncated_backprop_length, num_classes]), axis=1)
predictions_series = [tf.nn.softmax(logit) for logit in logits_series]


losses = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels)
total_loss = tf.reduce_mean(losses)

train_step = tf.train.AdagradOptimizer(0.3).minimize(total_loss)


def get_prediction(_predictions_series):
    one_hot_output_series = np.array(_predictions_series)[:, 0, :]
    single_output_series = np.array([(1 if out[0] < 0.5 else 0) for out in one_hot_output_series])
    return single_output_series

#running training
with tf.Session() as sess:
    sess.run(tf.initialize_all_variables())
    loss_list = []

    for epoch_idx in range(num_epochs):
        x,y = generateData()
        # _current_cell_state = np.zeros((batch_size, state_size))
        # _current_hidden_state = np.zeros((batch_size, state_size))
        _current_state = np.zeros((num_layers, 2, batch_size, state_size))

        print("New data, epoch", epoch_idx)

        for batch_idx in range(num_batches):
            start_idx = batch_idx * truncated_backprop_length
            end_idx = start_idx + truncated_backprop_length

            batchX = x[:,start_idx:end_idx]
            batchY = y[:,start_idx:end_idx]

            _total_loss, _train_step, _current_state, _predictions_series = sess.run(
                [total_loss, train_step, current_state, predictions_series],
                feed_dict={
                    batchX_placeholder:batchX,
                    batchY_placeholder:batchY,
                    init_state: _current_state
                })

            loss_list.append(_total_loss)

            if batch_idx%1000 == 0:
                print("Step",batch_idx, "Loss", _total_loss)
                print(batchX[0])
                print(batchY[0])
                print(get_prediction(_predictions_series))
