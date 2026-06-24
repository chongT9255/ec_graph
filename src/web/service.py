from langchain_classic.schema import output
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain, Neo4jVector
from neo4j_graphrag.types import SearchType

from configuration.config import *

class ChatService:
    """
    聊天服务类
    """
    def __init__(self):
        # 创建图数据库对象
        self.graph = Neo4jGraph(
            url=NEO4J_CONFIG['uri'],
            username=NEO4J_CONFIG['auth'][0],
            password=NEO4J_CONFIG['auth'][1]
        )
        # 嵌入模型
        self.embedding = HuggingFaceEmbeddings(
            model_name="BAAI/bge-base-zh-v1.5",
            encode_kwargs={"normalize_embeddings": True},  # 是否归一化嵌入向量
        )
        # LLM
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=API_KEY,
            # temperature=0,  # 模型温度，0表示最精确
        )
        # 定义所有实体对应的混合检索Neo4jVector对象
        self.neo4j_vector = {
            "Trademark": Neo4jVector.from_existing_index(
                self.embedding,
                url=NEO4J_CONFIG['uri'],
                username=NEO4J_CONFIG['auth'][0],
                password=NEO4J_CONFIG['auth'][1],
                index_name='trademark_vector_index',
                keyword_index_name='trademark_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            "SPU": Neo4jVector.from_existing_index(
                self.embedding,
                url=NEO4J_CONFIG['uri'],
                username=NEO4J_CONFIG['auth'][0],
                password=NEO4J_CONFIG['auth'][1],
                index_name='spu_vector_index',
                keyword_index_name='spu_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            "SKU": Neo4jVector.from_existing_index(
                self.embedding,
                url=NEO4J_CONFIG['uri'],
                username=NEO4J_CONFIG['auth'][0],
                password=NEO4J_CONFIG['auth'][1],
                index_name='sku_vector_index',
                keyword_index_name='sku_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            "Category1": Neo4jVector.from_existing_index(
                self.embedding,
                url=NEO4J_CONFIG['uri'],
                username=NEO4J_CONFIG['auth'][0],
                password=NEO4J_CONFIG['auth'][1],
                index_name='category1_vector_index',
                keyword_index_name='category1_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            "Category2": Neo4jVector.from_existing_index(
                self.embedding,
                url=NEO4J_CONFIG['uri'],
                username=NEO4J_CONFIG['auth'][0],
                password=NEO4J_CONFIG['auth'][1],
                index_name='category2_vector_index',
                keyword_index_name='category2_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            "Category3": Neo4jVector.from_existing_index(
                self.embedding,
                url=NEO4J_CONFIG['uri'],
                username=NEO4J_CONFIG['auth'][0],
                password=NEO4J_CONFIG['auth'][1],
                index_name='category3_vector_index',
                keyword_index_name='category3_fulltext_index',
                search_type=SearchType.HYBRID
            )
        }
        # 定义Parser
        self.json_parser = JsonOutputParser()
        self.str_parser = StrOutputParser()

    # 核心聊天服务流程
    def chat(self, question: str):
        # 1.根据用户问题，生成Cypher以及需要对齐的实体
        result = self._generate_cypher(question)
        cypher = result['cypher_query']
        entities_to_align = result['entities_to_align']
        print(cypher)
        print(f"对齐之后的实体名称：{entities_to_align}")

        # 2.实体对齐（混合检索）
        aligned_entities = self._entity_align(entities_to_align)
        print(f"对齐之后的实体名称：{aligned_entities}")

        # 3.执行Cypher语句，得到查询结果
        query_result = self._execute_cypher(cypher, aligned_entities)
        print(f"查询结果：{query_result}")

        # 4.根据用户问题和查询结果生成答案
        answer = self._generate_answer(question, query_result)
        print(f"最终回答：{answer}")
        return answer

    # 1.根据用户问题，调用LLM生成Cypher
    def _generate_cypher(self,question: str):
        template = """
            你是一个专业的Neo4j Cypher查询生成器。你的任务是根据用户问题生成一条Cypher查询语句，用于从知识图谱中获取回答用户问题所需的信息。
    
            用户问题：{question}
    
            知识图谱结构信息：{schema_info}
    
            要求：
            1. 生成参数化Cypher查询语句，用$param_0, $param_1等代替具体值（必须以$开头）
            2. 识别需要对齐的实体
            3. 必须严格使用以下JSON格式输出结果
            {{
              "cypher_query": "生成的Cypher语句",
              "entities_to_align": [
                {{
                  "param_name": "param_0",
                  "entity": "原始实体名称",
                  "label": "节点类型"
                }}
              ]
            }}
        """
        prompt = PromptTemplate.from_template( template)
        prompt = prompt.format(question=question, schema_info=self.graph.schema)
        # 得到模型输出
        output = self.llm.invoke(prompt)
        # 解析模型输出
        result = self.json_parser.invoke(output)
        return  result

    # 2.实体对齐（混合检索）
    def _entity_align(self, entities_to_align):
        # 遍历所有实体
        for index,entity_to_align in enumerate(entities_to_align):
            label = entity_to_align['label']
            entity = entity_to_align['entity']
            # 混合检索，得到对齐后的实体名称
            aligned_entity = self.neo4j_vector[label].similarity_search( entity, k=1)[0].page_content
            # 覆盖原来的实体名称
            entities_to_align[index]['entity'] = aligned_entity
        return entities_to_align

    # 3.用对齐的实体名称替换param_0,执行Cypher
    def _execute_cypher(self, cypher_query, aligned_entities):
        # 提取对齐后的实体名称
        params = {entity['param_name']: entity['entity'] for entity in aligned_entities}
        return self.graph.query(cypher_query, params=params)

    # 4.根据用户问题和查询结果生成答案
    def _generate_answer(self, question, query_result):
        prompt = """
        你是一个电商智能客服，根据用户问题，以及数据库查询结果生成一段简洁、准确的自然语言回答。
                用户问题: {question}
                数据库返回结果: {query_result}
        """
        prompt = prompt.format(question=question, query_result=query_result)
        output = self.llm.invoke(prompt)
        result = self.str_parser.invoke(output)
        return result

    def close(self):
        """关闭所有 Neo4j 连接"""
        self.graph._driver.close()
        for vector in self.neo4j_vector.values():
            vector._driver.close()

if __name__ == '__main__':
    chat_service = ChatService()
    chat_service.chat("Apple手机都有哪些产品")
    chat_service.close()