import cv2
import os
import base64
import requests
from typing import List, Dict, Any
from app.processors.base_processor import BaseProcessor
from app.config.settings import OLLAMA_BASE_URL, VISION_MODEL_LOCAL, DATA_DIR
from app.utils.logger import logger

class VideoProcessor(BaseProcessor):
    def extract_text(self, file_path: str) -> str:
        """Extrai descrição do vídeo através de frames chave usando modelo vision."""
        logger.info(f"Processando vídeo: {file_path}")
        temp_dir = DATA_DIR / "temp" / "frames"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        descriptions = []
        try:
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Extrai um frame a cada 5 segundos para vídeos longos
            interval = int(fps * 5) if fps > 0 else 30
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                
                if frame_count % interval == 0:
                    frame_path = temp_dir / f"frame_{frame_count}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    
                    # Descreve o frame usando o modelo vision
                    desc = self._describe_frame(str(frame_path))
                    if desc:
                        descriptions.append(f"[Tempo: {frame_count/fps:.1f}s]: {desc}")
                    
                    os.remove(frame_path)
                
                frame_count += 1
            cap.release()
            
            return f"Vídeo de {duration:.1f} segundos. Conteúdo:\n" + "\n".join(descriptions)
        except Exception as e:
            logger.error(f"Erro ao processar vídeo {file_path}: {e}")
            return ""

    def _describe_frame(self, frame_path: str) -> str:
        """Usa o modelo vision local para descrever um frame específico."""
        try:
            with open(frame_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": VISION_MODEL_LOCAL,
                    "prompt": "Descreva o que está acontecendo nesta cena de vídeo de forma concisa.",
                    "images": [img_b64],
                    "stream": False
                }
            )
            return response.json().get('response', '') if response.status_code == 200 else ""
        except:
            return ""

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados técnicos do vídeo."""
        try:
            cap = cv2.VideoCapture(file_path)
            meta = {
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "width": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                "height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                "frame_count": cap.get(cv2.CAP_PROP_FRAME_COUNT)
            }
            cap.release()
            return meta
        except:
            return {}
