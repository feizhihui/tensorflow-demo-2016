# encoding=utf-8


from __future__ import print_function

import tensorflow as tf
import input_data as load
import numpy as np

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data

img, label = load.read_and_decode('train.tfrecords')

# Parameters
learning_rate = 0.001
training_iters = 1000
batch_size = 128
display_step = 10
batch_size = 10

# Network Parameters
n_input = 2352  # MNIST data input (img shape: 28*28*3)
n_classes = 4  # MNIST total classes (0-3 digits)
dropout = 0.75  # Dropout, probability to keep units

# tf Graph input
x = tf.placeholder(tf.float32, [None, n_input])
y = tf.placeholder(tf.float32, [None, n_classes])
keep_prob = tf.placeholder(tf.float32)  # dropout (keep probability)


# Create some wrappers for simplicity
def conv2d(x, W, b, strides=1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)


def maxpool2d(x, k=2):
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                          padding='SAME')


# Create model
def conv_net(x, weights, biases, dropout):
    # Reshape input picture
    x = tf.reshape(x, shape=[-1, 28, 28, 3])

    # Convolution Layer
    conv1 = conv2d(x, weights['wc1'], biases['bc1'])
    # Max Pooling (down-sampling)
    conv1 = maxpool2d(conv1, k=2)

    # Convolution Layer
    conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
    # Max Pooling (down-sampling)
    conv2 = maxpool2d(conv2, k=2)

    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
    fc1 = tf.nn.relu(fc1)
    # Apply Dropout
    fc1 = tf.nn.dropout(fc1, dropout)

    # Output, class prediction
    out = tf.add(tf.matmul(fc1, weights['out']), biases['out'])
    return out


# Store layers weight & bias
weights = {
    # 5x5 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([5, 5, 3, 32])),
    # 5x5 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
    # fully connected, 7*7*64 inputs, 1024 outputs
    'wd1': tf.Variable(tf.random_normal([7 * 7 * 64, 1024])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([1024, n_classes]))
}

biases = {
    'bc1': tf.Variable(tf.random_normal([32])),
    'bc2': tf.Variable(tf.random_normal([64])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

# Construct model
pred = (conv_net(x, weights, biases, keep_prob))

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(pred, y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initializing the variables
init = tf.initialize_all_variables()
img_batch, label_batch = tf.train.shuffle_batch([img, label],
                                                batch_size=batch_size, capacity=2000,
                                                min_after_dequeue=1000)
# Launch the graph
with tf.Session() as sess:
    sess.run(init)
    # 启动队列
    threads = tf.train.start_queue_runners(sess=sess)
    step = 1
    # Keep training until reach max iterations
    while step * batch_size < training_iters:
        print('step:', step)

        batch_x, batch_y = sess.run([img_batch, label_batch])
        print('generated batch')
        print(batch_y)
        yarr = np.zeros(shape=[batch_size, n_classes])
        for k in range(batch_size):
            yarr[k][batch_y[k]] = 1
        batch_y = yarr
        # batch_x, batch_y = mnist.train.next_batch(batch_size)
        # Run optimization op (backprop)
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y,
                                       keep_prob: dropout})

        # if step % display_step == 0:
        if True:
            # Calculate batch loss and accuracy
            loss, acc = sess.run([cost, accuracy], feed_dict={x: batch_x,
                                                              y: batch_y,
                                                              keep_prob: 1.})
            print("Iter " + str(step * batch_size) + ", Minibatch Loss= " + \
                  "{:.6f}".format(loss) + ", Training Accuracy= " + \
                  "{:.5f}".format(acc))
        step += 1
    print("Optimization Finished!")

    batch_x, batch_y = sess.run([img_batch, label_batch])
    yarr = np.zeros(shape=[batch_size, n_classes])
    for k in range(batch_size):
        yarr[k][batch_y[k]] = 1
    batch_y = yarr

    # Calculate accuracy for 256 mnist test images
    b = sess.run([pred], feed_dict={x: batch_x,
                                          y: batch_y,
                                          keep_prob: 1.})


    print("Testing Accuracy:", b)
    print(batch_y)
    # print(sess.run(pred))
