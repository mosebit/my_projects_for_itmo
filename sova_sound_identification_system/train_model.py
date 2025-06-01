import os
# fix warning 'oneDNN custom operations are on'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import librosa
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.image import resize
from tensorflow.keras.models import load_model

# Step 2: Load and preprocess audio data
def load_and_preprocess_data(data_dir, classes, target_shape=(128, 128), whitelisted_classes=None):
    data = []
    labels = []

    for i, class_name in enumerate(classes):
        class_dir = os.path.join(data_dir, class_name)
        for filename in os.listdir(class_dir):
            if filename.endswith('.wav'):
                file_path = os.path.join(class_dir, filename)
                audio_data, sample_rate = librosa.load(file_path, sr=None)
                # Perform preprocessing (e.g., convert to Mel spectrogram and resize)
                mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
                mel_spectrogram = resize(np.expand_dims(mel_spectrogram, axis=-1), target_shape)
                data.append(mel_spectrogram)
                if whitelisted_classes is None:
                    labels.append(i)
                else:
                    if class_name in whitelisted_classes:
                        labels.append(1)
                    else:
                        labels.append(0)

    return np.array(data), np.array(labels)


def create_model(model_name: str, dir_with_sounds: str, whitelisted_classes=None):
    classes = os.listdir(dir_with_sounds)

    # Step 3: Split data into training and testing sets
    data, labels = load_and_preprocess_data(dir_with_sounds, classes, whitelisted_classes=whitelisted_classes)

    if whitelisted_classes is None:
        labels = to_categorical(labels, num_classes=len(classes))  # Convert labels to one-hot encoding
    else:
        labels = to_categorical(labels, num_classes=2)  # Convert labels to one-hot encoding

    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

    # Step 4: Create a neural network model
    input_shape = X_train[0].shape
    input_layer = Input(shape=input_shape)
    x = Conv2D(32, (3, 3), activation='relu')(input_layer)
    x = MaxPooling2D((2, 2))(x)
    x = Conv2D(64, (3, 3), activation='relu')(x)
    x = MaxPooling2D((2, 2))(x)
    x = Flatten()(x)
    x = Dense(64, activation='relu')(x)
    if whitelisted_classes is None:
        output_layer = Dense(len(classes), activation='softmax')(x)
    else:
        output_layer = Dense(2, activation='softmax')(x)

    model = Model(input_layer, output_layer)

    # Step 5: Compile the model
    #   learning_rate - This controls how much to adjust the model in response to the estimated error each time the
    #   model weights are updated.
    model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

    # Step 6: Train the model
    #   batch_size - This sets the number of samples per gradient update. It defines how many training
    #   examples you want to work through before updating the internal model parameters.
    #   25 - bin
    model.fit(X_train, y_train, epochs=25, batch_size=16, validation_data=(X_test, y_test))

    test_accuracy=model.evaluate(X_test,y_test,verbose=0)
    print(test_accuracy[1])

    # Step 7: Save the model
    model.save(f"{model_name}.h5")


create_model(model_name="binary",
             dir_with_sounds=r"C:\Users\Bazzz\Desktop\sova\main_datasets\all_categories",
             whitelisted_classes=["airplane", "drones", "fixed_wing_drones", "helicopter"]
             )
create_model(model_name="aircraft_classify",
             dir_with_sounds=r"C:\Users\Bazzz\Desktop\sova\main_datasets\only_aircrafts"
             )
