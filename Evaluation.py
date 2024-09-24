
############################### Insturction of use ###########################################
# * Model file path will be a string of path. Example:
pretrain_model_file_path = "/home/user/model.zip"
# This file is decompressed from (model_uid).zip file and being saved to this location.
# Please treat this as a string path to the file.

# * Dataset file path will be a string of path. Example:
training_dataset_file_path = "/home/user/dataset.zip"
# This file is decompressed from dataset.zip and being saved to this location.
# Please treat this as a string path to the file.

##############################################################################################

###### NOTE: CODES THAT PUT BEYOND THESE BLOCKS WILL BE IGNORED! ######

### USER IMPORT START ###
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

### USER CODE START ###
# Load pretrain model
model = load_model(pretrain_model_file_path)

# Get small split of trainig data
training_dataset = np.load(training_dataset_file_path, allow_pickle=True)
x = np.array([item[0] for item in training_dataset[:100]])
y = np.array([item[1] for item in training_dataset[:100]])

# Run evaluation
ret = model.evaluate(x, y, batch_size=4, return_dict=True)

## Please remember to set the name of return variable in the "pipeline_settings.json" file.