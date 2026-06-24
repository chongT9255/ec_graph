import pymysql
from neo4j import GraphDatabase
from pymysql.cursors import DictCursor

import main
from configuration.config import *


# 读取MYSQL工具类
class MysqlReader:
    """
    MYSQL工具类
    """
    def __init__(self):
        # 连接数据库,直接使用解包语法，将字典中的值分别传入参数
        self.connection = pymysql.connect(**MYSQL_CONFIG)
        # DictCursor: 将查询结果返回为字典
        self.cursor = self.connection.cursor(DictCursor)

    # 查询MySQL，读取数据
    def read(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.connection.close()


# 写入NEO4J工具类
class Neo4jWriter:
    """
    NEO4J工具类
    """
    def __init__(self):
        self.driver = GraphDatabase.driver(**NEO4J_CONFIG)

    # 写入节点(批量，固定标签)
    def write_nodes(self, label:str, properties:list[ dict]):
        cypher = f"""
                UNWIND $batch AS item
                MERGE (:{label} {{id:item.id, name:item.name}})
            """
        self.driver.execute_query(cypher, batch=properties)


    # 写入关系
    def write_relation(self, type:str,start_label:str, end_label:str, relations:list[ dict]):
        cypher = f"""
            UNWIND $batch AS item
            MATCH (start:{start_label} {{id:item.start_id}}) , (end:{end_label} {{id:item.end_id}})
            MERGE (start)-[:{type}]->(end)
            """
        self.driver.execute_query(cypher, batch=relations)



if __name__ == '__main__':
    # 创建MysqlReader对象
    mysql_reader = MysqlReader()
    # 创建Neo4jWriter对象
    writer = Neo4jWriter()

    # category1
    # 1、创建SQL语句
    sql = """
        select
            id,name
        from
            base_category1
    """
    # 执行SQL语句
    category1 = mysql_reader.read(sql)
    # 打印结果
    print(category1)
    # 2、写入neo4j
    # for item in category1:
    #     # 创建节点
    #     cypher = """
    #         MERGE (n:CateGory1 {id:$id,name:$name})
    #     """
    #     # 执行SQL语句
    #     driver.execute_query(cypher,parameters_=item)
    # cypher = """
    #     UNWIND $category1 AS item
    #     MERGE (:Category1 {id:item.id, name:item.name})
    # """
    # driver.execute_query(cypher,category1=category1)
    writer.write_nodes("Category1",category1)


    # category2
    # 1、创建SQL语句
    sql = """
          select id,
                 name
          from base_category2
          """
    # 执行SQL语句
    category2 = mysql_reader.read(sql)
    # 打印结果
    print(category2)

    # cypher = """
    #         UNWIND $category2 AS item
    #         MERGE (:Category2 {id:item.id, name:item.name})
    #     """
    # driver.execute_query(cypher, category2=category2)
    writer.write_nodes("Category2", category2)

    # 连接关系 category2 -Belong-> category1
    # 1、创建SQL语句
    sql = """
          select id as start_id,
                 category1_id as end_id
          from base_category2
          """
    relations = mysql_reader.read(sql)
    print(relations)
    # cypher = """
    #         UNWIND $relations AS item
    #         MATCH (start:Category2 {id:item.start_id}) , (end:Category1 {id:item.end_id})
    #         MERGE (start)-[:Belong]->(end)
    #     """
    # driver.execute_query(cypher, relations=relations)
    writer.write_relation("Belong", "Category2", "Category1", relations)