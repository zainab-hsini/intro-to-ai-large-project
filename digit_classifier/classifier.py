import tensorflow as tf
import numpy as np
import json
from pathlib import Path


class DigitClassifier:

    def __init__(self):
        # Locate the saved model and configuration
        directory = Path(__file__).resolve().parent

        # Load the trained ConvNet model
        self.model = tf.keras.models.load_model(
            directory / "digit_classifier.keras",
            compile=False
        )

        # Load the selected confidence threshold
        with open(directory / "classifier_config.json", "r") as file:
            config = json.load(file)

        self.threshold = config["confidence_threshold"]

    def classify_digit(self, image):
        # Preprocess the MNIST image
        image = np.asarray(image, dtype=np.float32)
        image = image.reshape(1, 28 * 28) / 255.0

        # Generate class probabilities
        probabilities = self.model(image, training=False).numpy()[0]

        # Extract predicted digit and confidence
        prediction = int(np.argmax(probabilities))
        confidence = float(np.max(probabilities))

        # Determine whether the prediction should be accepted
        accepted = confidence >= self.threshold

        return prediction, confidence, accepted