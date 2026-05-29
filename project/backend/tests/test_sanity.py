from collections import Counter


def test_sanity_check():
    predictions = [
        {"pred_label": "APP_LOGIN", "confidence": 0.88},
        {"pred_label": "PAYMENT_OUT_FAIL", "confidence": 0.81},
        {"pred_label": "CARD_ISSUE", "confidence": 0.79},
        {"pred_label": "APP_LOGIN", "confidence": 0.74},
    ]

    labels = [item["pred_label"] for item in predictions]
    confidences = [item["confidence"] for item in predictions]

    assert len(set(labels)) > 1
    assert Counter(labels).most_common(1)[0][1] < len(labels)
    assert all(0.0 <= confidence <= 1.0 for confidence in confidences)

