from utils import MysqlReader,Neo4jWriter


# 构建一个表数据的同步器
class TableSynchronizer:
    def __init__(self):
        # 创建MysqlReader对象
        self.mysql_reader = MysqlReader()
        # 创建Neo4jWriter对象
        self.neo4j_writer = Neo4jWriter()

    # 1.分类信息
    def sync_category1(self):
        sql = """
            select
                id,name
            from
                base_category1
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("Category1",properties)


    def sync_category2(self):
        sql = """
            select
                id,name
            from
                base_category2
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("Category2",properties)

    def sync_category3(self):
        sql = """
            select
                id,name
            from
                base_category3
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("Category3",properties)

    # 从下级分类表中，提取与上级分类的关系
    def sync_category2_to_category1(self):
        sql = """
          select id as start_id,
                 category1_id as end_id
          from base_category2
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Belong", "Category2", "Category1", relations)

    def sync_category3_to_category2(self):
        sql = """
          select id as start_id,
                 category2_id as end_id
          from base_category3
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Belong", "Category3", "Category2", relations)

    # 2.平台属性
    def sync_base_attr_name(self):
        sql = """
            select
                id,
                attr_name as name
            from
                base_attr_info
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("BaseAttrName",properties)

    def sync_base_attr_value(self):
        sql = """
            select
                id,
                value_name as name
            from
                base_attr_value
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("BaseAttrValue",properties)

    def sync_base_attr_name_to_value(self):
        sql = """
            select
                id as end_id,
                attr_id as start_id
            from
                base_attr_value
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "BaseAttrName", "BaseAttrValue",relations)

    # 类别到属性关系，三个可以考虑合成一个

    def sync_category1_to_base_attr_name(self):
        sql = """
            select
                id as end_id,
                category_id as start_id
            from
                base_attr_info
            where category_level = 1
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "Category1", "BaseAttrName",relations)

    def sync_category2_to_base_attr_name(self):
        sql = """
            select
                id as end_id,
                category_id as start_id
            from
                base_attr_info
            where category_level = 2
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "Category2", "BaseAttrName",relations)


    def sync_category3_to_base_attr_name(self):
        sql = """
            select
                id as end_id,
                category_id as start_id
            from
                base_attr_info
            where category_level = 3
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "Category3", "BaseAttrName",relations)

    # 3.商品信息
    def sync_spu(self):
        sql = """
            select id,
                spu_name as name
            from spu_info
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("SPU",properties)

    def sync_sku(self):
        sql = """
            select id,
                sku_name as name
            from sku_info
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("SKU",properties)

    # 商品信息关系
    def sync_sku_to_spu(self):
        sql = """
            select
                id as start_id,
                spu_id as end_id
            from
                sku_info
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Belong", "SKU", "SPU",relations)

    def sync_spu_to_category3(self):
        sql = """
            select
                id as start_id,
                category3_id as end_id
            from
                spu_info
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Belong", "SPU", "Category3",relations)

    # 4.品牌信息
    def sync_trademark(self):
        sql = """
            select
                id,
                tm_name as name
            from
                base_trademark
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("Trademark",properties)

    # 关系
    def sync_spu_to_trademark(self):
        sql = """
            select
                id as start_id,
                tm_id as end_id
            from
                spu_info
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Belong", "SPU", "Trademark",relations)

    # 5.销售属性
    def sync_sale_attr_name(self):
        sql = """
            select
                id,
                sale_attr_name as name
            from
                spu_sale_attr
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("SaleAttrName",properties)

    def sync_sale_attr_value(self):
        sql = """
            select
                id,
                sale_attr_value_name as name
            from
                spu_sale_attr_value
        """
        properties = self.mysql_reader.read(sql)
        self.neo4j_writer.write_nodes("SaleAttrValue",properties)

    # 销售属性关系
    def sync_sale_attr_name_to_value(self):
        sql = """
            select 
                a.id as start_id,
                v.id as end_id 
            from spu_sale_attr a 
            join spu_sale_attr_value v
                on a.spu_id = v.spu_id
                and a.base_sale_attr_id = v.base_sale_attr_id
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "SaleAttrName", "SaleAttrValue",relations)

    def sync_spu_to_sale_attr_name(self):
        sql = """
            select
                spu_id as start_id,
                id as end_id
            from spu_sale_attr 
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "SPU", "SaleAttrName",relations)

    def sync_sku_to_sale_attr_value(self):
        sql = """
            select
                sku_id as start_id,
                sale_attr_value_id as end_id
            from sku_sale_attr_value
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "SKU", "SaleAttrValue",relations)

    def sync_sku_to_base_attr_value(self):
        sql = """
            select
                sku_id as start_id,
                value_id as end_id
            from sku_attr_value
        """
        relations = self.mysql_reader.read(sql)
        self.neo4j_writer.write_relation("Have", "SKU", "BaseAttrValue",relations)

if __name__ == '__main__':
    synchronizer = TableSynchronizer()
    # 同步分类信息
    synchronizer.sync_category1()
    synchronizer.sync_category2()
    synchronizer.sync_category3()
    synchronizer.sync_category2_to_category1()
    synchronizer.sync_category3_to_category2()
    # 同步平台属性信息
    synchronizer.sync_base_attr_name()
    synchronizer.sync_base_attr_value()
    synchronizer.sync_base_attr_name_to_value()
    synchronizer.sync_category1_to_base_attr_name()
    synchronizer.sync_category2_to_base_attr_name()
    synchronizer.sync_category3_to_base_attr_name()
    # 同步商品信息
    synchronizer.sync_spu()
    synchronizer.sync_sku()
    synchronizer.sync_trademark()
    synchronizer.sync_sku_to_spu()
    synchronizer.sync_spu_to_category3()
    synchronizer.sync_spu_to_trademark()

    # 同步销售属性信息
    synchronizer.sync_sale_attr_name()
    synchronizer.sync_sale_attr_value()
    synchronizer.sync_sale_attr_name_to_value()
    synchronizer.sync_spu_to_sale_attr_name()
    synchronizer.sync_sku_to_sale_attr_value()
    synchronizer.sync_sku_to_base_attr_value()
