from noise_reducer import reduce_noise
from illumination_normalizer import normalize_illumination
from contrast_checker import check_low_contrast
from grayscale_converter import convert_to_grayscale

class ImagePreprocessor:
    def __init__(self, config):
        self.config = config
        self.steps = {
            "noise_reduction": reduce_noise,
            "illumination_normalization": normalize_illumination,
            "grayscale_conversion": convert_to_grayscale,
        }

    def preprocess(self, image):
        for step_name, params in self.config.get("steps", {}).items():
            if step_name in self.steps:
                if step_name == "noise_reduction":
                    image = self.steps[step_name](image, **params)
                elif step_name == "illumination_normalization":
                    image = self.steps[step_name](image, **params)
                elif step_name == "grayscale_conversion":
                    image = self.steps[step_name](image)
        return image

    def check_contrast(self, image):
        contrast_config = self.config.get("contrast_check", {})
        threshold = contrast_config.get("threshold", 0.35)
        return check_low_contrast(image, threshold=threshold)
