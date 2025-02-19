from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())
print("---------------------------------------------")
import tensorflow as tf
print(tf.test.is_built_with_cuda())
print("---------------------------------------------")
import tensorflow as tf
# Get the list of all physical devices
physical_devices = tf.config.experimental.list_physical_devices('GPU')
print(physical_devices)
