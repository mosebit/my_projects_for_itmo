import os
# fix warning 'oneDNN custom operations are on'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import yt_dlp
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
from pydub import AudioSegment
from playsound import playsound


def get_filename_from_url(url: str):
    main_start_pos = url.find('www.youtube.com')
    if main_start_pos == -1:
        print('Error: url doesnt contain \'www.youtube.com\'!')
        return -1
    id_start_pos = main_start_pos + len('www.youtube.com\\')
    # название видео - все, что находится после 'https://www.youtube.com/' (сделано это для того, чтобы потом можно было восстановить ссылку)
    video_name = url[id_start_pos:].replace('\\', '_').replace('/', '_').replace('=', '_').replace('?', '_')
    return video_name


class SystemTester:
    def __init__(self,
                 binary_model_path: str,
                 classify_model_path: str,
                 size_of_pieces,
                 path_for_saving_sounds: str
                 ):
        self.binary_model = load_model(binary_model_path)
        self.classify_model = load_model(classify_model_path)
        self.path_for_saving_sounds = path_for_saving_sounds
        self.size_of_pieces = size_of_pieces
        self.successful_downloads, self.failed_downloads, self.failed_video_ids = [], [], []

        self.binary_classes = ['other', 'aircraft']
        self.aircraft_classes = ['airplane', 'drones', 'fixed_wing_drones', 'helicopter']

        self.target_shape = (128, 128)

        # проверка папки, в которой будут сохраняться звуки, использующиеся для тестов
        if not os.path.exists(self.path_for_saving_sounds):
            os.makedirs(self.path_for_saving_sounds)
        else:
            if os.listdir(self.path_for_saving_sounds):
                print("Error: path for saving sounds is not empty!")
                raise ValueError

    def download_sound_from_youtube(self, video_url):
        # получаем название видео
        video_name = get_filename_from_url(url=video_url)
        if video_name == -1:
            return -1

        path_to_files = self.path_for_saving_sounds + '\\' + str(video_name) + '\\'
        if not os.path.exists(path_to_files):
            os.makedirs(path_to_files)
        file_path = path_to_files + '\\raw'

        ydl_opts = {
            'format': 'bestaudio/best',  # Select the best audio quality
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Extract audio using FFmpeg
                'preferredcodec': 'wav',  # Save audio in wav format
                'preferredquality': '192',  # Set audio quality
            }],
            'outtmpl': file_path,  # Output file template
            'quiet': True,  # Suppress output messages
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([video_url])
                print("Downloaded:", video_url, "to", file_path)
                self.successful_downloads.append(video_url)
                return video_name
            except Exception as e:
                print(f"Failed to download {video_url}: {e}")
                self.failed_downloads.append(video_url)
                self.failed_video_ids.append(video_name)
                return None

    def check_sound_by_models(self, file_path):
        # Load and preprocess the audio file
        audio_data, sample_rate = librosa.load(file_path, sr=None)
        mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
        mel_spectrogram = resize(np.expand_dims(mel_spectrogram, axis=-1), self.target_shape)
        mel_spectrogram = tf.reshape(mel_spectrogram, (1,) + self.target_shape + (1,))

        # Make predictions - binary
        predictions = self.binary_model.predict(mel_spectrogram)
        # Get the class probabilities
        binary_class_probabilities = predictions[0]
        # Get the predicted class index
        predicted_class_index = np.argmax(binary_class_probabilities)

        binary_probability = binary_class_probabilities[predicted_class_index]
        # TODO вывести все вероятности по результату работы обеих моделей
        if binary_class_probabilities[1] > 0.4:
            aircraft_class = self.classify_model.predict(mel_spectrogram)
            class_probabilities = aircraft_class[0]
            predicted_aircraft_class_index = np.argmax(class_probabilities)
            print(f"Aircraft sound found:\n\tProbability of aircraft: {binary_probability}\n\t"
                  f"Type of aircraft: {self.aircraft_classes[predicted_aircraft_class_index]}, "
                  f"accuracy: {class_probabilities[predicted_aircraft_class_index]}.")
        else:
            print(f"No aircraft sound - predicted_class_index: {predicted_class_index}, binary_probability: {binary_probability}")

    def test_sound(self, sound_name: str):
        sound_path = self.path_for_saving_sounds + f'\\{sound_name}\\raw.wav'
        duration = librosa.get_duration(path=sound_path)

        # проверяем продолжительность аудио в секундах и делим одну запись на множество отрезков
        if duration > self.size_of_pieces:
            # находим количество отрезков, на которые нужно разделить, используется округление в большую строноу
            count_of_parts = int(duration / self.size_of_pieces) + (duration % self.size_of_pieces > 0)
            # находим длину последнего отрезка
            last_part_duration = duration - int(duration / self.size_of_pieces) * self.size_of_pieces
            # если длина последнего отрезка меньше обычного, то его не учитываем
            if last_part_duration < self.size_of_pieces: count_of_parts -= 1

            try:
                raw_sound = AudioSegment.from_wav(sound_path)
            except:
                print("Error in AudioSegment.from_wav")
                return -1

            for i in range(count_of_parts):
                start_time = i * self.size_of_pieces * 1000
                end_time = (i + 1) * self.size_of_pieces * 1000
                new_sound = raw_sound[start_time:end_time]

                # path_for_results = f'{cutted_files_folder}\\{subdirs}\\{i}{file}'

                # вырезаем из строки основную часть, чтобы заменить путь на путь к новой папке
                path_for_dir_with_results = self.path_for_saving_sounds + f'\\{sound_name}\\fixed'
                res_path_for_result = f'{path_for_dir_with_results}\\{i}_{sound_name}.wav'
                print(f"res_path_for_result:{res_path_for_result}")

                if not os.path.exists(path_for_dir_with_results):
                    os.makedirs(path_for_dir_with_results)

                new_sound.export(res_path_for_result, format="wav")
                self.check_sound_by_models(file_path=res_path_for_result)
                # playsound(res_path_for_result, True)
        elif duration < self.size_of_pieces:
            print("Error: duration < self.size_of_pieces")


working_dir = r'C:\Users\Bazzz\Desktop\owl\main_model\tests_tmp_folders'
test_system = SystemTester(binary_model_path='binary.h5',
                           classify_model_path='aircraft_classify.h5',
                           size_of_pieces=5,
                           path_for_saving_sounds=working_dir
                           )
sound_name = test_system.download_sound_from_youtube(
    video_url='https://www.youtube.com/watch?v=dNg7uhHFCDs&ab_channel=ourthings'
)
test_system.test_sound(sound_name=sound_name)
