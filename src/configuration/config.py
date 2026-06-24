from pathlib import Path
import os

# 1.目录路径
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
NER_DIR = 'ner'
RAW_DATA_DIR = DATA_DIR / NER_DIR /'raw'
PROCESSED_DATA_DIR = DATA_DIR / NER_DIR /'processed'

LOG_DIR = ROOT_DIR / 'logs'
CHECKPOINT_DIR = ROOT_DIR / 'checkpoints'
# web 静态目录
WEB_STATIC_DIR = ROOT_DIR / 'src' / 'web' / 'static'

# 2.数据文件名和模型名称
RAW_DATA_FILE = str(RAW_DATA_DIR / 'data.json')
MODEL_NAME = "google-bert/bert-base-chinese"

# 3.超参数
BATCH_SIZE = 2 # 批次大小，目前数据量少，设置较小的批次大小
EPOCHS = 5
LEARNING_RATE = 5e-5

SAVE_STEPS = 20  # 每20步保存一次模型

# 4.NER任务分类标签
LABELS = ["B","I","O"]  # BIO标注方案，B表示实体开始，I表示实体内部，O表示非实体

# 5.数据库连接
MYSQL_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '12345',
    'db': 'gmall',
    'charset': 'utf8mb4'
}

NEO4J_CONFIG = {
    'uri': "neo4j://localhost:7687",
    'auth': ("neo4j", "12345678")
}

API_KEY = os.getenv("API_KEY", "")



