from pathlib import Path

import torch
from howl.client import HowlClient
from howl.context import InferenceContext
from howl.data.transform import ZmuvTransform
from howl.model import RegisteredModel, Workspace, workspace
from howl.model.inference import FrameInferenceEngine, SequenceInferenceEngine

class WakeDetector():
    def __init__(self, model_name, samplerate=8000):
        if model_name not in RegisteredModel.registered_names():
           raise ValueError('Unknown model')
        
        ws = Workspace(Path(str(Path('workspaces') / 'default')), delete_existing=False)
        settings = ws.load_settings()

        use_frame = settings.training.objective == 'frame'
        ctx = InferenceContext(settings.training.vocab, token_type=settings.training.token_type, use_blank=not use_frame)

        device = torch.device(settings.training.device)
        zmuv_transform = ZmuvTransform().to(device)
        model = RegisteredModel.find_registered_class(model_name)(ctx.num_labels).to(device).eval()
        zmuv_transform.load_state_dict(torch.load(str(ws.path / 'zmuv.pt.bin'), map_location=device))

        ws.load_model(model, best=True)
        model.streaming()
        if use_frame:
            engine = FrameInferenceEngine(
                int(settings.training.max_window_size_seconds * 1000),
                int(settings.training.eval_stride_size_seconds * 1000),
                model,
                zmuv_transform,
                ctx,
            )
        else:
            engine = SequenceInferenceEngine(model, zmuv_transform, ctx)
        
        client = HowlClient(engine, ctx)
        client.start().join()

    def detect(self):
        self.wrdRec.record2File('wakeword_temp.wav')
        return self.hwDet.isHotword('wakeword_temp.wav')
