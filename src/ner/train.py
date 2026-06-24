import os
import time

from datasets import load_dataset, load_from_disk
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, \
    DataCollatorForTokenClassification, EvalPrediction, EarlyStoppingCallback

from configuration.config import *

os.environ["TENSORBOARD_LOGGING_DIR"] = str(LOG_DIR / NER_DIR/time.strftime('%Y-%m-%d-%H-%M-%S'))

# 1.分词器
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# 标签映射
id2label = {id:label for id,label in enumerate(LABELS)}
label2id = {label: id for id, label in enumerate(LABELS)}

# 2.模型
model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(LABELS),
    id2label=id2label,
    label2id=label2id
)

# 3.数据集
train_dataset = load_from_disk(PROCESSED_DATA_DIR/'train')
val_dataset = load_from_disk(PROCESSED_DATA_DIR/'val')

# 4.数据整理器
data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    padding=True,
    return_tensors= "pt",
)

# 5.训练参数
args = TrainingArguments(
    output_dir=str(CHECKPOINT_DIR/NER_DIR),# 模型保存目录
    # logging_dir=str(LOG_DIR/NER_DIR/time.strftime('%Y-%m-%d-%H-%M-%S')),
    report_to="tensorboard",

    num_train_epochs=EPOCHS, # 训练轮数
    per_device_train_batch_size=BATCH_SIZE, # 批次大小

    save_strategy="steps",# 每20步保存一次
    save_steps=SAVE_STEPS, # 保存模型的频率
    save_total_limit=3, # 最多保存3个检查点

    fp16=True, # 使用混合精度训练（如果支持的话）

    logging_strategy="steps", # 日志写入策略
    logging_steps=SAVE_STEPS, # 每20步记录一次日志

    eval_strategy="steps", # 每20步评估一次模型
    eval_steps=SAVE_STEPS, # 评估模型的频率

    metric_for_best_model="eval_overall_f1", # 评估指标，选择F1分数作为评估指标
    greater_is_better=True, # F1分数越高越好
    load_best_model_at_end=True, # 训练结束后加载最佳模型
)

# 6.评估器
import evaluate
seqeval = evaluate.load("seqeval" )

# 评估函
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
        unpad_label = [id2label[id] for id in unpad_label]
        unpad_pred = [id2label[id] for id in unpad_pred]
        # 添加到列表中
        unpad_labels.append(unpad_label)
        unpad_preds.append(unpad_pred)
    # 计算评估指标
    return seqeval.compute(predictions=unpad_preds, references=unpad_labels)

# 7.早停回调
early_stopping_callback = EarlyStoppingCallback(early_stopping_patience=20) # 如果连续20次评估指标没有提升，则停止训练

# 创建训练器
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator, # 数据整理器，负责将输入数据整理成模型所需的格式
    compute_metrics=compute_metrics,
    callbacks=[early_stopping_callback], # 早停回调
)
# 训练
trainer.train()


# 5.模型保存
trainer.save_model(CHECKPOINT_DIR/NER_DIR/'best_model.pt')















