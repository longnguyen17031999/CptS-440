# detect.py <image>
#
# See https://keras.io/api/applications/inceptionresnetv2/ for details.

# Need numpy, tensorflow, pillow package to work

from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input, decode_predictions

import numpy as np
import sys

img_path = sys.argv[1]
img = image.load_img(img_path, target_size=(299, 299))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

model = InceptionResNetV2()
predictions = model.predict(x)
# A prediction is a (class, description, probability) tuple
for prediction in decode_predictions(predictions, top=10)[0]:
    print(str(prediction[1]) + ', ' + str(prediction[2]))
