from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

from configuration.config import *

graph = Neo4jGraph(url=NEO4J_CONFIG['uri'],
                   username=NEO4J_CONFIG['auth'][0],
                   password=NEO4J_CONFIG['auth'][1]
                   )
# print( graph.schema)


# 查询
cypher = "MATCH (n) RETURN n LIMIT 5"
result = graph.query(cypher)
print(result)

from langchain_deepseek import ChatDeepSeek
# 定义大模型
llm = ChatDeepSeek(
    model = "deepseek-chat",
    api_key = API_KEY,
    temperature = 0, # 模型温度，0表示最精确
)
chain = GraphCypherQAChain.from_llm(llm=llm, graph=graph, verbose=True,allow_dangerous_requests=True)
result = chain.invoke({"query": "HUAWEI有什么产品？"})