# import os
# os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from dotenv import load_dotenv
load_dotenv()

from datasets import load_dataset
from transformers import AutoTokenizer

from configuration.config import *

def process():
    # 1.读取数据
    dataset = load_dataset('json', data_files=RAW_DATA_FILE)['train']
    # print( dataset)
    # 2.去除多余列
    dataset = dataset.remove_columns(['id',  'annotator', 'annotation_id', 'created_at', 'updated_at', 'lead_time'])
    # 3.划分训练集和验证集
    dataset_dict = dataset.train_test_split(test_size=0.2, seed=42)
    dataset_dict['test'], dataset_dict['val'] = dataset_dict['test'].train_test_split(test_size=0.5, seed=42).values()

    # 4.定义分词器
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # 5.数据编码
    def encode(example):
        # 1.将文本数据转成字符列表
        tokens = list(example['text'])
        # 2.文本编码
        inputs = tokenizer(
            tokens,
            truncation=True,
            is_split_into_words=True
        )

        # 3.进行实体标注
        entities = example['label']
        # 定义标注列表,存放id，默认都为O的id
        labels = [LABELS.index("O")] * len(tokens)
        # 遍历每个TAG，标记为B和I的id
        for entity in entities:
            start = entity['start']
            end = entity['end']
            labels[start:end] = [LABELS.index("B")] + [LABELS.index("I")] * (end - start - 1)
        # 前后加上id = -100 ，对应CLS和SEP的标签，训练时会被忽略
        labels = [-100] + labels + [-100]
        inputs['labels'] = labels
        return inputs

    dataset_dict = dataset_dict.map(encode,remove_columns=['text', 'label'])
    print(dataset_dict['train'][0])
    # 6.保存数据
    dataset_dict.save_to_disk(PROCESSED_DATA_DIR)

if __name__ == '__main__':
    process()















