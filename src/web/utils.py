from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain, Neo4jVector
from neo4j_graphrag.types import SearchType

from configuration.config import *

class IndexUtil:
    """
    索引工具类
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
            encode_kwargs={"normalize_embeddings": True}, # 是否归一化嵌入向量

        )


    # 创建全文索引,传入索引名称，节点标签，属性
    def create_fulltext_index(self, index_name:str, label:str, property:str):
        cypher = f"""
            CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS
            FOR (n:{label}) ON EACH [n.{property}]
        """
        self.graph.query(cypher) # 执行Cypher语句

    # 创建向量索引，需要传入生成向量的“原属性”，以及嵌入向量属性
    def create_vector_index(self, index_name:str, label:str, source_property:str ,embedding_property:str):
        # 生成嵌入向量，并添加到节点属性中
        embedding_dim =self._add_embedding(label, source_property, embedding_property)

        cypher = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (n:{label})
            ON (n.{embedding_property})
            OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: {embedding_dim},
                `vector.similarity_function`: 'cosine'
            }}
            }}
        """
        self.graph.query(cypher)

    # 内部函数：生成嵌入向量，并添加到节点属性中，返回向量维度
    def _add_embedding(self, label:str,source_property:str, embedding_property:str):
        # 1.查询所有节点对应的源属性值，作为模型的输入；还需要节点ID
        cypher = f"""
            MATCH (n:{label}) 
            RETURN n.{source_property} AS text, elementId(n) AS id
        """

        results = self.graph.query(cypher)

        # 2.获取查询结果中的文本内容
        docs = [result['text'] for result in results]

        # 3.调用嵌入模型，得到嵌入向量
        embeddings = self.embedding.embed_documents(docs)

        # 4.将id和嵌入向量组合成字典形式
        batch = []
        for result, embedding in zip(results, embeddings):
            item = {
                "id": result['id'],
                embedding_property: embedding
            }
            batch.append(item)

        # 5.执行cypher，按id查节点，写入写的嵌入向量属性
        cypher = f"""
            UNWIND $batch AS item
            MATCH (n:{label}) 
            WHERE elementId(n) = item.id
            SET n.{embedding_property} = item.embedding
        """
        self.graph.query(cypher, params={"batch": batch})
        return len(embeddings[0])

if __name__ == '__main__':
    index_util = IndexUtil()

    # ====== 品牌索引 ======
    # 已注释，需要时取消注释
    # index_util.create_fulltext_index("trademark_fulltext_index", "Trademark", "name")
    # index_util.create_vector_index("trademark_vector_index", "Trademark", "name", "embedding")

    # ====== 商品索引 ======
    # SPU 全文索引 + 向量索引
    index_util.create_fulltext_index("spu_fulltext_index", "SPU", "name")
    index_util.create_vector_index("spu_vector_index", "SPU", "name", "embedding")
    # SKU 全文索引 + 向量索引
    index_util.create_fulltext_index("sku_fulltext_index", "SKU", "name")
    index_util.create_vector_index("sku_vector_index", "SKU", "name", "embedding")

    # ====== 类别索引 ======
    # Category1 全文索引 + 向量索引
    index_util.create_fulltext_index("category1_fulltext_index", "Category1", "name")
    index_util.create_vector_index("category1_vector_index", "Category1", "name", "embedding")
    # Category2 全文索引 + 向量索引
    index_util.create_fulltext_index("category2_fulltext_index", "Category2", "name")
    index_util.create_vector_index("category2_vector_index", "Category2", "name", "embedding")
    # Category3 全文索引 + 向量索引
    index_util.create_fulltext_index("category3_fulltext_index", "Category3", "name")
    index_util.create_vector_index("category3_vector_index", "Category3", "name", "embedding")

    # 关闭驱动连接
    index_util.graph._driver.close()






