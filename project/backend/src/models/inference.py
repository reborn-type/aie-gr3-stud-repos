from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from settings import get_path


MODEL_DIR = get_path("final_model_dir")


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

def load_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_DIR)

def load_model():
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    model.to(get_device())
    model.eval()
    return model


def predict_label(title: str, text: str, tokenizer, model) -> dict:
    appeal = title + " " + text
    encoded = tokenizer(
        appeal,
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )

    encoded = {key: value.to(model.device) for key, value in encoded.items()}

    with torch.inference_mode():
        outputs = model(**encoded)
        probs = torch.softmax(outputs.logits, dim=-1)
        confidence, pred_id = torch.max(probs, dim=-1)

    pred_id = int(pred_id.item())

    row = {
        "appeal": appeal,
        "pred_label": model.config.id2label[pred_id],
        "confidence": float(confidence.item()),
    }

    return row
