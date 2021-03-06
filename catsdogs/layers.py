import theano
from theano import tensor
import numpy
from theano.tensor.nnet.conv import conv2d
from theano.tensor.signal.downsample import max_pool_2d
from theano.tensor.nnet import relu


def convolutional(X, X_test, input_shape, n_filters, filter_size):
	"""
	Implementation of a convolutional layer

	Parameters
	----------
	X
	input_shape
	n_filters
	filter_size

	Note
	----
	The convolutions are implemented using border_mode=same, that is the 
	output shape is the same as the input shape for the 2 last dimensions
	"""

	filters_shape = (n_filters, input_shape[1], filter_size[0], filter_size[1])
	filters = theano.shared(
		numpy.random.uniform(low=-0.1, high=0.1, size=filters_shape).astype(numpy.float32),
		'conv_filters'
	)

	output_shape = (input_shape[0], n_filters, input_shape[2], input_shape[3])

	output = conv2d(input=X, filters=filters, filter_shape=filters_shape, image_shape=input_shape, border_mode='full')
	output_test = conv2d(input=X_test, filters=filters, filter_shape=filters_shape, image_shape=input_shape, border_mode='full')

	shift_x = (filter_size[0] - 1) // 2
	shift_y = (filter_size[1] - 1) // 2

	output = output[:,:,shift_x:input_shape[2]+shift_x,shift_y:input_shape[3]+shift_y]
	output_test = output_test[:,:,shift_x:input_shape[2]+shift_x,shift_y:input_shape[3]+shift_y]

	return output, output_test, [filters], output_shape

def maxpool(X, X_test, input_shape, size):
	"""
	A maxpool layer
	"""

	pooled = max_pool_2d(input=X, ds=size, ignore_border=True)
	pooled_test = max_pool_2d(input=X_test, ds=size, ignore_border=True)
	output_shape = (input_shape[0], input_shape[1], input_shape[2]/size[0], input_shape[3]/size[1])

	return pooled, pooled_test, [], output_shape


def linear(X, X_test, input_shape, output_size):
	"""
	A simple linear layer output = W.X + b
	"""

	W = theano.shared(
		numpy.random.uniform(low=-0.1, high=0.1, size=(input_shape[1], output_size)).astype(numpy.float32),
		'linear_weights'
	)
	b = theano.shared(numpy.zeros(output_size).astype(numpy.float32))

	output = tensor.dot(X, W) + b
	output_test = tensor.dot(X_test, W) + b
	output_shape = (input_shape[0], output_size)

	return output, output_test, [W, b], output_shape

def activation(X, X_test, input_shape, activation_type='relu'):

	if activation_type=='relu':
		output = relu(X)
		output_test = relu(X_test)
	elif activation_type=='sigmoid':
		output = tensor.nnet.sigmoid(X)
		output_test = tensor.nnet.sigmoid(X_test)

	else:
		raise Exception('this non linearity does not exist: %s' % activation_type)

	return output, output_test, [], input_shape

def dropout(X, X_test, input_shape, p=0.5):

    srng = tensor.shared_randomstreams.RandomStreams()

    # p=1-p because 1's indicate keep and p is prob of dropping
    mask = srng.binomial(n=1, p=1-p, size=input_shape)

    # The cast is important because
    # int * float32 = float64 which pulls things off the gpu
    output = X * tensor.cast(mask, theano.config.floatX)
    output_test = X_test

    return output, output_test, [], input_shape