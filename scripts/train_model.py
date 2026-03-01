#!/usr/bin/env python3
"""
Script d'entraînement pour créer un modèle wakeword personnalisé avec openWakeWord.

Usage:
    python scripts/train_model.py --phrase "ok bollard" --name "ok_bollard"
    python scripts/train_model.py --help
"""

import argparse
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
MODELS_DIR = SCRIPT_DIR / "models"
DATA_DIR = SCRIPT_DIR / "data"
NEGATIVE_DATA_DIR = DATA_DIR / "negative"
POSITIVE_DATA_DIR = DATA_DIR / "positive"

DEFAULT_POSITIVE_SAMPLES = 3000
DEFAULT_NEGATIVE_SAMPLES = 5000


def check_dependencies():
    required = ["torch", "torchaudio", "numpy", "datasets", "piper_tts"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"Dépendances manquantes: {', '.join(missing)}")
        logger.info("Installez-les avec: pip install " + " ".join(missing))
        return False
    return True


def setup_directories():
    for directory in [MODELS_DIR, DATA_DIR, NEGATIVE_DATA_DIR, POSITIVE_DATA_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def generate_positive_samples(phrase: str, n_samples: int = DEFAULT_POSITIVE_SAMPLES):
    import numpy as np
    import soundfile as sf
    
    try:
        from piper_tts import PiperTTS
    except ImportError:
        logger.error("piper_tts non installé. Installez avec: pip install piper-tts")
        return False
    
    logger.info(f"Génération de {n_samples} échantillons pour '{phrase}'...")
    
    output_dir = POSITIVE_DATA_DIR / phrase.replace(" ", "_")
    output_dir.mkdir(exist_ok=True)
    
    piper = PiperTTS()
    
    variations = [
        phrase,
        phrase.lower(),
        phrase.upper(),
    ]
    
    for i in range(n_samples):
        phrase_variant = variations[i % len(variations)]
        
        audio = piper.generate(phrase_variant)
        
        if audio is not None:
            audio_int16 = (audio * 32767).astype(np.int16)
            sf.write(output_dir / f"sample_{i:05d}.wav", audio_int16, 16000)
        
        if (i + 1) % 500 == 0:
            logger.info(f"  Progression: {i+1}/{n_samples}")
    
    logger.info(f"Échantillons positifs générés dans: {output_dir}")
    return True


def download_negative_samples(n_samples: int = DEFAULT_NEGATIVE_SAMPLES):
    from datasets import load_dataset
    
    logger.info(f"Téléchargement de {n_samples} échantillons négatifs...")
    
    try:
        dataset = load_dataset(
            "mozilla-foundation/common_voice_17_0",
            "fr",
            split="train",
            streaming=True,
        )
    except Exception as e:
        logger.warning(f"Erreur CommonVoice FR: {e}, tentative en anglais...")
        try:
            dataset = load_dataset(
                "mozilla-foundation/common_voice_17_0",
                "en",
                split="train",
                streaming=True,
            )
        except Exception as e2:
            logger.error(f"Impossible de charger les données: {e2}")
            return False
    
    output_dir = NEGATIVE_DATA_DIR
    output_dir.mkdir(exist_ok=True)
    
    count = 0
    for i, sample in enumerate(dataset):
        if count >= n_samples:
            break
        
        try:
            audio = sample["audio"]["array"]
            if audio is not None:
                import numpy as np
                import soundfile as sf
                
                audio_int16 = (audio * 32767).astype(np.int16)
                sf.write(
                    output_dir / f"negative_{i:05d}.wav",
                    audio_int16,
                    sample["audio"]["sampling_rate"],
                )
                count += 1
                
                if count % 500 == 0:
                    logger.info(f"  Progression: {count}/{n_samples}")
        except Exception as e:
            logger.debug(f"Erreur sur sample {i}: {e}")
            continue
    
    logger.info(f"Échantillons négatifs téléchargés dans: {output_dir}")
    return True


def train_model(phrase: str, model_name: str, epochs: int = 25):
    import numpy as np
    import torch
    import torchaudio
    from torch.utils.data import DataLoader, Dataset
    
    logger.info(f"Entraînement du modèle '{model_name}' pour {epochs} epochs...")
    
    positive_dir = POSITIVE_DATA_DIR / phrase.replace(" ", "_")
    negative_dir = NEGATIVE_DATA_DIR
    
    if not positive_dir.exists() or not list(positive_dir.glob("*.wav")):
        logger.error("Pas de données positives. Exécutez d'abord generate_positive_samples")
        return False
    
    if not negative_dir.exists() or not list(negative_dir.glob("*.wav")):
        logger.error("Pas de données négatives. Exécutez d'abord download_negative_samples")
        return False
    
    class AudioDataset(Dataset):
        def __init__(self, positive_dir, negative_dir, sample_rate=16000):
            self.samples = []
            self.sample_rate = sample_rate
            
            for wav_path in positive_dir.glob("*.wav"):
                self.samples.append((wav_path, 1))
            
            negative_files = list(negative_dir.glob("*.wav"))
            for wav_path in negative_files[:len(self.samples) * 2]:
                self.samples.append((wav_path, 0))
        
        def __len__(self):
            return len(self.samples)
        
        def __getitem__(self, idx):
            wav_path, label = self.samples[idx]
            waveform, sr = torchaudio.load(wav_path)
            
            if sr != self.sample_rate:
                waveform = torchaudio.functional.resample(waveform, sr, self.sample_rate)
            
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            
            return waveform, label
    
    dataset = AudioDataset(positive_dir, negative_dir)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    class SimpleWakewordModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = torch.nn.Conv1d(1, 32, kernel_size=3, padding=1)
            self.conv2 = torch.nn.Conv1d(32, 64, kernel_size=3, padding=1)
            self.pool = torch.nn.MaxPool1d(2)
            self.fc1 = torch.nn.Linear(64 * 40, 128)
            self.fc2 = torch.nn.Linear(128, 1)
            self.dropout = torch.nn.Dropout(0.3)
        
        def forward(self, x):
            x = torch.relu(self.conv1(x))
            x = self.pool(x)
            x = torch.relu(self.conv2(x))
            x = self.pool(x)
            x = x.view(x.size(0), -1)
            x = torch.relu(self.fc1(x))
            x = self.dropout(x)
            x = torch.sigmoid(self.fc2(x))
            return x
    
    model = SimpleWakewordModel()
    criterion = torch.nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(epochs):
        total_loss = 0
        correct = 0
        total = 0
        
        for waveforms, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(waveforms)
            loss = criterion(outputs.squeeze(), labels.float())
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            predicted = (outputs.squeeze() > 0.5).float()
            total += labels.size(0)
            correct += (predicted == labels.float()).sum().item()
        
        accuracy = 100 * correct / total
        logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(dataloader):.4f} - Accuracy: {accuracy:.1f}%")
    
    model_path = MODELS_DIR / f"{model_name}.pth"
    torch.save(model.state_dict(), model_path)
    
    try:
        import torch.onnx
        dummy_input = torch.randn(1, 1, 16000)
        onnx_path = MODELS_DIR / f"{model_name}.onnx"
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_path),
            input_names=["audio"],
            output_names=["prediction"],
            dynamic_axes={"audio": {0: "batch"}, "prediction": {0: "batch"}},
        )
        logger.info(f"Modèle ONNX exporté: {onnx_path}")
    except Exception as e:
        logger.warning(f"Export ONNX échoué: {e}")
    
    logger.info(f"Modèle entraîné et sauvegardé: {model_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Entraîner un modèle wakeword personnalisé avec openWakeWord",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
    # Générer les données positives (phrase cible)
    python scripts/train_model.py --phrase "ok bollard" --generate-positive

    # Télécharger les données négatives
    python scripts/train_model.py --download-negative

    # Entraîner le modèle
    python scripts/train_model.py --phrase "ok bollard" --name "ok_bollard" --train

    # Pipeline complet
    python scripts/train_model.py --phrase "ok bollard" --name "ok_bollard" --all
        """,
    )
    
    parser.add_argument("--phrase", type=str, help="Phrase wakeword cible")
    parser.add_argument("--name", type=str, help="Nom du modèle (sans extension)")
    parser.add_argument("--generate-positive", action="store_true", help="Générer les données positives")
    parser.add_argument("--download-negative", action="store_true", help="Télécharger les données négatives")
    parser.add_argument("--train", action="store_true", help="Entraîner le modèle")
    parser.add_argument("--all", action="store_true", help="Exécuter le pipeline complet")
    parser.add_argument("--n-positive", type=int, default=DEFAULT_POSITIVE_SAMPLES, help="Nombre d'échantillons positifs")
    parser.add_argument("--n-negative", type=int, default=DEFAULT_NEGATIVE_SAMPLES, help="Nombre d'échantillons négatifs")
    parser.add_argument("--epochs", type=int, default=25, help="Nombre d'epochs")
    
    args = parser.parse_args()
    
    if not args.phrase and not args.download_negative:
        parser.print_help()
        return
    
    setup_directories()
    
    if not check_dependencies():
        sys.exit(1)
    
    if args.all or args.generate_positive:
        if not args.phrase:
            logger.error("--phrase requis pour générer les données positives")
            sys.exit(1)
        generate_positive_samples(args.phrase, args.n_positive)
    
    if args.all or args.download_negative:
        download_negative_samples(args.n_negative)
    
    if args.all or args.train:
        if not args.phrase or not args.name:
            logger.error("--phrase et --name requis pour l'entraînement")
            sys.exit(1)
        train_model(args.phrase, args.name, args.epochs)


if __name__ == "__main__":
    main()
