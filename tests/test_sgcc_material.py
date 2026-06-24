import unittest

from src.sgcc_material import ProcurementPipeline
from src.sgcc_material.sample_texts import SAMPLE_PROCUREMENT_TEXT


class ProcurementPipelineTest(unittest.TestCase):
    def test_extracts_customer_json_blocks(self):
        result = ProcurementPipeline().extract(SAMPLE_PROCUREMENT_TEXT, "sample")

        self.assertIn("复合绝缘子", result.material_categories)
        self.assertGreaterEqual(len(result.qualification_requirements), 2)
        self.assertGreaterEqual(len(result.rule_strategies), 2)
        self.assertGreaterEqual(len(result.business_review_criteria), 2)
        self.assertGreaterEqual(len(result.technical_review_criteria), 2)

        first = result.qualification_requirements[0]
        self.assertEqual(first.material_category, "复合绝缘子")
        self.assertIn("有效型式试验报告", "".join(first.test_report))

    def test_graph_and_hybrid_retrieval(self):
        pipeline = ProcurementPipeline()
        result = pipeline.extract(SAMPLE_PROCUREMENT_TEXT, "sample")
        graph = pipeline.build_graph(result)
        retriever = pipeline.build_retriever(result)

        self.assertTrue(any(node.label == "Material" for node in graph.nodes.values()))
        hits = retriever.search("复合绝缘子 420kN 型式试验报告", top_k=3)
        self.assertTrue(hits)
        self.assertIn("qualification", hits[0].doc_id)


if __name__ == "__main__":
    unittest.main()
