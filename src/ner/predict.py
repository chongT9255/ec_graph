import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

from configuration.config import *


# 自定义预测器类
class Predictor():
    # 初始化方法，接收模型、分词器、设备
    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def predict(self, inputs:str| list[str]):
        """
        预测方法，接收输入文本，返回预测结果
        """
        # 如果是一条数据，转换为列表处理
        is_str = isinstance(inputs, str)
        if is_str:
            inputs = [inputs]
        # 1.预分词，得到字符列表
        tokens_list = [list(input) for input in inputs]
        # 2.用分词器id化处理
        input_tensor = self.tokenizer(
            tokens_list,
            is_split_into_words=True,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        # 3.将数据移到指定设备
        input_tensor = {key:value.to(self.device) for key, value in input_tensor.items()}
        # 4.模型预测
        with torch.no_grad():
            logits = self.model(**input_tensor).logits
            predictions = logits.argmax(dim=-1).tolist()
        # 5.将预测结果转换为BIO标签
        final_predictions = []
        for tokens,prediction in zip(tokens_list,predictions):
            # 截取预测输出中，真实长度
            prediction = prediction[1:len(tokens)+1]
            # 遍历每个标签，转换为BIO标签
            final_prediction = [self.model.config.id2label[id] for id in prediction]
            final_predictions.append(final_prediction)

        if is_str:
            return final_predictions[0]

        return final_predictions

    # 抽取实体
    def extract(self, inputs:str| list[str]):
        """
        抽取实体
        :param inputs:
        :return:
        """
        # 如果是一条数据，转换为列表处理
        is_str = isinstance(inputs, str)
        if is_str:
            inputs = [inputs]

        # 得到预测标签列表
        predictions = self.predict(inputs)
        # 从当前列表中，舟曲实体列表
        entities_list = []
        for input,labels in zip(inputs,predictions):
            # 调用内部函数，抽取一个数据样本的所有实体标签
            entities = self._extract_entities(list(input),labels)
            entities_list.append(entities)
        if is_str:
            return entities_list[0]

        return entities_list

    def _extract_entities(self,tokens,labels):
        entities = []
        current_entity = ""
        for token,label in zip(tokens,labels):
            # 如果是B标签，则开始一个新的实体
            if label == "B":
                if current_entity:
                    entities.append(current_entity)
                current_entity = token
            # 如果是I标签，则继续添加实体
            elif label == "I":
                if current_entity:
                    current_entity += token
            # 如果是O标签，则将当前实体(如果存在)添加到列表中
            else:
                if current_entity:
                    entities.append(current_entity)
                current_entity = ""
        # 添加最后一个实体
        if current_entity:
            entities.append(current_entity)

        return  entities



def predict():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForTokenClassification.from_pretrained( str(CHECKPOINT_DIR/NER_DIR/'best_model.pt'))
    tokenizer = AutoTokenizer.from_pretrained(str(CHECKPOINT_DIR/NER_DIR/'best_model.pt'))
    # 定义预测器
    predictor = Predictor(model=model, tokenizer=tokenizer, device=device)
    # 定义数据
    text = ["麦德龙德国进口双心多维叶黄素护眼营养软胶囊30粒x3盒眼干涩","热风2018年秋季时尚女士运动风休闲鞋深口系带单鞋h11w8103"]
    # # 预测
    # result = predictor.predict(text)
    # for token,label in zip(text,result):
    #     print(token,label)

    # 抽取实体
    entities = predictor.extract(text)
    print(entities)


if __name__ == '__main__':
    predict()











