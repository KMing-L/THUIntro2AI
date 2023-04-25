from transformers import Trainer, TrainingArguments
import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast, AutoTokenizer, AutoModelForSequenceClassification
from data_reader import getLLMData
import evaluate
import numpy as np

train_texts, train_labels = getLLMData('dataset/train.txt')
val_texts, val_labels = getLLMData('dataset/validation.txt')
test_texts, test_labels = getLLMData('dataset/test.txt')

# tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

train_encodings = tokenizer(
    train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)
test_encodings = tokenizer(test_texts, truncation=True, padding=True)


class BertDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx])
                for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_dataset = BertDataset(train_encodings, train_labels)
val_dataset = BertDataset(val_encodings, val_labels)
test_dataset = BertDataset(test_encodings, test_labels)


training_args = TrainingArguments(
    output_dir='./saved',          # output directory
    num_train_epochs=3,              # total # of training epochs
    per_device_train_batch_size=16,  # batch size per device during training
    per_device_eval_batch_size=16,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./logs',            # directory for storing logs
    logging_steps=10,
)

model = AutoModelForSequenceClassification.from_pretrained(
    './saved/checkpoint-3000')
# model = DistilBertForSequenceClassification.from_pretrained(
#     "distilbert-base-uncased")
# model = AutoModelForSequenceClassification.from_pretrained(
#     "bert-base-chinese")

trainer = Trainer(
    # the instantiated 🤗 Transformers model to be trained
    model=model,
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset,          # evaluation dataset
)

# trainer.train()

# trainer.evaluate()

predictions, label, _ = trainer.predict(test_dataset)

clf_metrics = evaluate.combine(["accuracy", "f1", "precision", "recall"])
result = clf_metrics.compute(np.argmax(predictions, axis=1), test_labels)

print(result)
