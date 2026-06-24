from transformers import Trainer

import os
import time

from datasets import load_dataset, load_from_disk
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, \
    DataCollatorForTokenClassification, EvalPrediction, EarlyStoppingCallback

from configuration.config import *

os.environ["TENSORBOARD_LOGGING_DIR"] = str(LOG_DIR / NER_DIR/time.strftime('%Y-%m-%d-%H-%M-%S'))

# 1.分词器
tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT_DIR/NER_DIR/'best_model.pt')


# 2.模型
model = AutoModelForTokenClassification.from_pretrained(CHECKPOINT_DIR / NER_DIR / 'best_model.pt')

# 3.数据集
test_dataset = load_from_disk(PROCESSED_DATA_DIR/'test')

# 4.数据整理器
data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    padding=True,
    return_tensors= "pt",
)

# 5.评估器
import evaluate
seqeval = evaluate.load("seqeval" )

# 评估函数
def compute_metrics(prediction: EvalPrediction):
    logits = prediction.predictions
    preds = logits.argmax( axis=-1) # 获取预测结果
    labels = prediction.label_ids # 获取真实标签
    # 将标签id转换为实体标签列表
    unpad_labels = []
    unpad_preds = []
    for label, pred in zip(labels, preds):
        # 去掉填充对应的id
        unpad_label = label[label != -100]
        unpad_pred = pred[label != -100]
        # 转换成实体标签列表
        unpad_label = [model.config.id2label[id] for id in unpad_label]
        unpad_pred = [model.config.id2label[id] for id in unpad_pred]
        # 添加到列表中
        unpad_labels.append(unpad_label)
        unpad_preds.append(unpad_pred)
    # 计算评估指标
    return seqeval.compute(predictions=unpad_preds, references=unpad_labels)



# 6.定义训练器
trainer = Trainer(
    model=model,
    eval_dataset=test_dataset,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# 7.验证评估
result = trainer.evaluate()

print(result)















