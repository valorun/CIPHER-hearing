import logging
import os
from pathlib import Path

import numpy as np
import openwakeword
from openwakeword.model import Model

from .config import client_config

logger = logging.getLogger(__name__)


class WakeDetector:
    def __init__(
        self,
        model_paths: list[str] | None = None,
        threshold: float = 0.5,
        vad_threshold: float | None = None,
        enable_speex: bool = False,
        samplerate: int = 16000,
    ):
        self.samplerate = samplerate
        self.threshold = threshold

        models_to_load = model_paths or []
        
        if not models_to_load:
            default_models_dir = Path.home() / ".local" / "share" / "openwakeword" / "models"
            if default_models_dir.exists():
                models_to_load = [
                    str(p) for p in default_models_dir.glob("*.tflite")
                ]
        
        logger.info(f"Loading openwakeword models: {models_to_load}")

        model_kwargs = {
            "wakeword_model_paths": models_to_load,
            "enable_speex_noise_suppression": enable_speex,
        }
        if vad_threshold is not None:
            model_kwargs["vad_threshold"] = vad_threshold

        self.model = Model(**model_kwargs)

    def detect(self, data: bytes) -> float | None:
        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0

        prediction = self.model.predict(audio_data)

        for model_name, score in prediction.items():
            if score >= self.threshold:
                logger.debug(f"Wakeword '{model_name}' detected with score {score:.4f}")
                return score

        return None

    @staticmethod
    def download_models(models: list[str] | None = None) -> None:
        openwakeword.utils.download_models(models=models)


def create_wake_detector(config) -> WakeDetector:
    model_paths = []
    
    if hasattr(config, 'WAKEWORD_MODELS') and config.WAKEWORD_MODELS:
        model_names = [m.strip() for m in config.WAKEWORD_MODELS.split(',')]
        models_dir = Path(__file__).parent.parent / "models"
        
        for model_name in model_names:
            model_path = models_dir / f"{model_name}.tflite"
            if model_path.exists():
                model_paths.append(str(model_path))
            else:
                logger.warning(f"Model not found: {model_path}")

    vad_threshold = getattr(config, 'VAD_THRESHOLD', None)
    if vad_threshold is not None:
        vad_threshold = float(vad_threshold)

    return WakeDetector(
        model_paths=model_paths if model_paths else None,
        threshold=config.WAKEWORD_THRESHOLD,
        vad_threshold=vad_threshold,
        samplerate=config.SAMPLERATE,
    )
