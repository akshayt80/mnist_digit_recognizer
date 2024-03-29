from __future__ import print_function

import tensorflow as tf
import numpy as np
from sklearn.metrics import confusion_matrix
import time
from datetime import timedelta
import math
import data_set
import csv
import data_set1

from tensorflow.examples.tutorials.mnist import input_data


data, test_set = data_set.read_files()

# Convolutional Layer 1.
filter_size1 = 5
num_filters1 = 36

# Convolutional Layer 2.
filter_size2 = 5
num_filters2 = 64

# Convolutional layer 3
filter_size3 = 2
num_filters3 = 128

# Convolutional layer 4
filter_size4 = 2
num_filters4 = 256

# Fully-connected layer.
fc_size = 512

img_size = 28
img_size_flat = img_size * img_size
img_shape = (img_size, img_size)
channels = 1
num_classes = 10

total_iterations = 0
test_batch_size = 256

def new_weights(shape):
    return tf.Variable(tf.truncated_normal(shape, stddev=0.05))

def new_biases(length):
    return tf.Variable(tf.constant(0.05, shape=[length]))

def conv_layer(input,
                   num_input_channels,
                   filter_size,
                   num_filters,
                   pooling=True):

    shape = [filter_size, filter_size, num_input_channels, num_filters]

    weights = new_weights(shape=shape)

    biases = new_biases(length=num_filters)

    layer = tf.nn.conv2d(input=input,
                         filter=weights,
                         strides=[1, 1, 1, 1],
                         padding='SAME')

    
    layer += biases

    if pooling:
        layer = tf.nn.max_pool(value=layer,
                               ksize=[1, 2, 2, 1],
                               strides=[1, 2, 2, 1],
                               padding='SAME')

    layer = tf.nn.relu(layer)

    return layer, weights

def flatten_layer(layer):
    layer_shape = layer.get_shape()

    num_features = layer_shape[1:4].num_elements()
    
    layer_flat = tf.reshape(layer, [-1, num_features])

    return layer_flat, num_features

def fc_layer(input,
             num_inputs,
             num_outputs,
             relu=True):

    # Create new weights and biases.
    weights = new_weights(shape=[num_inputs, num_outputs])
    biases = new_biases(length=num_outputs)

    layer = tf.matmul(input, weights) + biases

    if relu:
        layer = tf.nn.relu(layer)

    return layer

def main():

    def optimize(num_iterations):
        
        global total_iterations

        start_time = time.time()

        for i in range(total_iterations,
                       total_iterations + num_iterations):

            # Get a batch of training examples.
            x_batch, y_true_batch = data.train.next_batch(train_batch_size)

            feed_dict_train = {x: x_batch,
                               y_true: y_true_batch}
           
            session.run(optimizer, feed_dict=feed_dict_train)

            # Print status every 100 iterations.
            if i % 100 == 0:
                acc = session.run(accuracy, feed_dict=feed_dict_train)
                msg = "Optimization Iteration: {0:>6}, Training Accuracy: {1:>6.1%}"
                print(msg.format(i + 1, acc))

        total_iterations += num_iterations
        end_time = time.time()
        time_dif = end_time - start_time
        print("Time usage: " + str(timedelta(seconds=int(round(time_dif)))))

    def print_test_accuracy():

        num_test = len(data.test.images)
        cls_pred = np.zeros(shape=num_test, dtype=np.int)

        i = 0
        while i < num_test:
            
            j = min(i + test_batch_size, num_test)
            images = data.test.images[i:j, :]
            labels = data.test.labels[i:j, :]
            feed_dict = {x: images,
                         y_true: labels}
            cls_pred[i:j] = session.run(y_pred_cls, feed_dict=feed_dict)
            i = j

        cls_true = data.test.cls
        correct = (cls_true == cls_pred)

        # Calculate the number of correctly classified images.
        # When summing a boolean array, False means 0 and True means 1.
        correct_sum = correct.sum()
        acc = float(correct_sum) / num_test
        msg = "Accuracy on Test-Set: {0:.1%} ({1} / {2})"
        print(msg.format(acc, correct_sum, num_test))

    def run_test():
        num_test = len(test_set)
        cls_pred = np.zeros(shape=num_test, dtype=np.int)
        i = 0
        imageid = 0
        result_list = [["imageid", "label"]]

        while i < num_test:
            j = min(i + test_batch_size, num_test)
            images = test_set[i:j, :]
            feed_dict = {x: images}
            cls_pred[i:j] = session.run(y_pred_cls, feed_dict=feed_dict)
            for index in range(i, j):
                imageid+=1
                result_list.append([imageid, cls_pred[index]])
            i=j
        with open("test_result.csv", "w") as test_file:
            writer = csv.writer(test_file)
            writer.writerows(result_list)

    print ("Size of:")
    print ("- Training-set:", len(data.train.labels))
    print ("- Validation-set:", len(data.validation.labels))
    
    data.test.cls = np.argmax(data.test.labels, axis=1)
    cls_true = data.test.cls[0:9]
    print (cls_true)

    x = tf.placeholder(tf.float32, shape=[None, img_size_flat], name='x')
    x_image = tf.reshape(x, [-1, img_size, img_size, channels])
    y_true = tf.placeholder(tf.float32, shape=[None, 10], name='y_true')
    y_true_cls = tf.argmax(y_true, dimension=1)
    
    #layer1
    layer_conv1, weights_conv1 = \
    conv_layer(input=x_image,
                   num_input_channels=channels,
                   filter_size=filter_size1,
                   num_filters=num_filters1,
                   pooling=True)
    #layer2
    layer_conv2, weights_conv2 = \
    conv_layer(input=layer_conv1,
                   num_input_channels=num_filters1,
                   filter_size=filter_size2,
                   num_filters=num_filters2,
                   pooling=False)

    #layer3
    layer_conv3, weights_conv3 = \
    conv_layer(input=layer_conv2,
                   num_input_channels=num_filters2,
                   filter_size=filter_size3,
                   num_filters=num_filters3,
                   pooling=False)
    #layer4
    layer_conv4, weights_conv4 = \
    conv_layer(input=layer_conv3,
                   num_input_channels=num_filters3,
                   filter_size=filter_size4,
                   num_filters=num_filters4,
                   pooling=False)

    layer_flat, num_features = flatten_layer(layer_conv4)

    print ("number of features:", num_features)

    layer_fc1 = fc_layer(input=layer_flat,
                         num_inputs=num_features,
                         num_outputs=fc_size,
                         relu=True)

    layer_fc2 = fc_layer(input=layer_fc1,
                         num_inputs=fc_size,
                         num_outputs=num_classes,
                         relu=False)

    y_pred = tf.nn.softmax(layer_fc2)
    y_pred_cls = tf.argmax(y_pred, dimension=1)

    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=layer_fc2,
                                                        labels=y_true)

    cost = tf.reduce_mean(cross_entropy)
    optimizer = tf.train.AdamOptimizer(learning_rate=1e-3).minimize(cost)

    correct_prediction = tf.equal(y_pred_cls, y_true_cls)

    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    session = tf.Session()
    session.run(tf.global_variables_initializer())
    train_batch_size = 64

    optimize(num_iterations=9000)
    print_test_accuracy()
    run_test()
if __name__ == '__main__':
    main()
