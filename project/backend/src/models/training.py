import random 
from typing import Dict, List
from pathlib import Path
import sys
import matplotlib.pyplot as plt

from datasets import Dataset, DatasetDict
import numpy as np 
import pandas as pd 
import torch 
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from transformers import AutoTokenizer, DataCollatorWithPadding, Trainer, TrainingArguments, AutoModelForSequenceClassification

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from settings import get_path, load_yaml_config

DATASET_PATH = get_path("dataset")
ARTIFACTS_DIR = get_path("artifacts_dir")
FINAL_MODEL_DIR = get_path("final_model_dir")
FIGURES_DIR = get_path("figures_dir")

CONFIG = load_yaml_config("main_model_config.yaml")
MODEL_CONFIG = CONFIG["model"]
SPLIT_CONFIG = CONFIG["split"]
TRAINING_CONFIG = CONFIG["training"]

RANDOM_STATE = CONFIG["random_state"]
MODEL_NAME = MODEL_CONFIG["name"]
MAX_LENGTH = MODEL_CONFIG["max_length"]

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(RANDOM_STATE)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print(f'Tokenizer class: {tokenizer.__class__.__name__}')
print(f'Tokenizer max length: {tokenizer.model_max_length}')

df = pd.read_csv(DATASET_PATH, sep=";")

print(df['label'].value_counts())

label_names = df['label'].unique()
label2id = {label: idx for idx, label in enumerate(label_names)}
id2label = {idx: label for label, idx in label2id.items()}

df['label_id'] = df['label'].map(label2id)

train_df, test_df = train_test_split(
    df, 
    test_size=SPLIT_CONFIG["test_size"], 
    random_state=RANDOM_STATE, 
    stratify=df['label_id'],
)

train_df, val_df = train_test_split(
    train_df,
    test_size=SPLIT_CONFIG["validation_size"],
    random_state=RANDOM_STATE, 
    stratify=train_df['label_id'],
)


train_ds = Dataset.from_pandas(
    train_df[['text', 'label_id']].rename(columns={'label_id': 'labels'}).reset_index(drop=True),
    preserve_index=False,
)

val_ds = Dataset.from_pandas(
    val_df[['text', 'label_id']].rename(columns={'label_id': 'labels'}).reset_index(drop=True),
    preserve_index=False, 
)

test_ds = Dataset.from_pandas(
    test_df[['text', 'label_id']].rename(columns={'label_id': 'labels'}).reset_index(drop=True),
    preserve_index=False, 
)

dataset_dict = DatasetDict({
    "train": train_ds, 
    "validation": val_ds, 
    "test": test_ds, 
})


def tokenize_batch(batch: Dict[str, List[str]]) -> Dict[str, List[List[int]]]:
    return tokenizer(
        batch['text'],
        truncation=True, 
        max_length=MAX_LENGTH,
    )
    
tokenized_datasets = dataset_dict.map(tokenize_batch, batched=True)
tokenized_datasets = tokenized_datasets.remove_columns(["text"])

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

sample_batch = [tokenized_datasets['train'][i] for i in range(3)]
collated_batch = data_collator(sample_batch)

for key, value in collated_batch.items():
    print(f"{key}: shape={tuple(value.shape)}")
    
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(label_names),
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True,
)

model.to(device)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    
    acc = accuracy_score(labels, preds)
    f1_macro = f1_score(labels, preds, average='macro')
    f1_weighted = f1_score(labels, preds, average='weighted')
    
    return {
        'accuracy': acc,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted
    }
    

common_training_params = dict(
    output_dir=str(ARTIFACTS_DIR / 'bert_finetuning'),
    learning_rate=float(TRAINING_CONFIG["learning_rate"]), 
    per_device_train_batch_size=TRAINING_CONFIG["train_batch_size"],
    per_device_eval_batch_size=TRAINING_CONFIG["eval_batch_size"], 
    num_train_epochs=TRAINING_CONFIG["epochs"], 
    weight_decay=0.01, 
    logging_steps=TRAINING_CONFIG["logging_steps"], 
    save_total_limit=1, 
    load_best_model_at_end=True, 
    metric_for_best_model='f1_macro',
    greater_is_better=True,
    report_to='none',
)

try:
    training_args = TrainingArguments(
        evaluation_strategy='epoch',
        save_strategy="epoch",
        **common_training_params,
    )
except TypeError: 
    training_args = TrainingArguments(
        eval_strategy="epoch",
        save_strategy="epoch",
        **common_training_params,
    )

try: 
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        processing_class=tokenizer, 
        data_collator=data_collator,
        compute_metrics=compute_metrics, 
    )
except TypeError:
    trainer=Trainer(
        model=model, 
        args=training_args,
        train_dataset=tokenized_datasets['train'],
        eval_dataset=tokenized_datasets['validation'],
        tokenizer=tokenizer, 
        data_collator=data_collator, 
        compute_metrics=compute_metrics,
    )
    
train_results = trainer.train()
print(train_results)

FINAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
trainer.save_model(FINAL_MODEL_DIR)
tokenizer.save_pretrained(FINAL_MODEL_DIR)

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

history_df = pd.DataFrame(trainer.state.log_history)
print(history_df.head(10))

plt.figure(figsize=(8, 4))

if "loss" in history_df.columns:
    train_logs = history_df.dropna(subset=["loss"])
    plt.plot(train_logs["step"], train_logs["loss"], marker="o", label="train loss")

if "eval_loss" in history_df.columns:
    eval_logs = history_df.dropna(subset=["eval_loss"])
    plt.plot(eval_logs["step"], eval_logs["eval_loss"], marker="s", label="eval loss")

plt.title("История обучения")
plt.xlabel("Шаг")
plt.ylabel("Loss")
plt.grid(True, alpha=0.3)
plt.legend()

plt.savefig(FIGURES_DIR / "train_loss_eval_loss.png", dpi=300, bbox_inches="tight")

from transformers.utils.notebook import NotebookProgressCallback
trainer.remove_callback(NotebookProgressCallback)

val_metrics = trainer.evaluate(tokenized_datasets["validation"])
test_metrics = trainer.evaluate(tokenized_datasets["test"])

print("Validation metrics:")
for k, v in val_metrics.items():
    print(f"{k}: {v:.4f}" if isinstance(v, (int, float)) else f"{k}: {v}")

print("\nTest metrics:")
for k, v in test_metrics.items():
    print(f"{k}: {v:.4f}" if isinstance(v, (int, float)) else f"{k}: {v}")
