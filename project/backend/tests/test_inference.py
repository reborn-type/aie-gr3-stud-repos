from types import SimpleNamespace

import torch

from models.inference import predict_label


class FakeTokenizer:
    def __call__(self, text, return_tensors, truncation, max_length):
        assert text == "Login problem Password does not work"
        assert return_tensors == "pt"
        assert truncation is True
        assert max_length == 256

        return {
            "input_ids": torch.tensor([[101, 102]]),
            "attention_mask": torch.tensor([[1, 1]]),
        }


class FakeModel:
    device = torch.device("cpu")
    config = SimpleNamespace(id2label={0: "APP_LOGIN", 1: "PAYMENT_OUT_FAIL"})

    def __call__(self, **inputs):
        assert set(inputs) == {"input_ids", "attention_mask"}
        return SimpleNamespace(logits=torch.tensor([[3.0, 1.0]]))


def test_predict_returning():
    result = predict_label(
        title="Login problem",
        text="Password does not work",
        tokenizer=FakeTokenizer(),
        model=FakeModel(),
    )

    assert result["appeal"] == "Login problem Password does not work"
    assert result["pred_label"] == "APP_LOGIN"
    assert 0.0 <= result["confidence"] <= 1.0

