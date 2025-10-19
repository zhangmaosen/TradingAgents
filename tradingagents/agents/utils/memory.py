
import chromadb
from chromadb.config import Settings
from openai import OpenAI

from zai import ZhipuAiClient
import os
from dotenv import load_dotenv
load_dotenv()


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.use_bigmodel = False
        if "open.bigmodel.cn" in config["backend_url"]:
            self.use_bigmodel = True
            self.embedding = "embedding-3"
            api_key = os.getenv("ZHIPU_API_KEY")
            if not api_key:
                raise ValueError("ZHIPU_API_KEY environment variable is not set. Please set it in your .env file.")
            self.client = ZhipuAiClient(api_key=api_key)
        elif "11434" in config["backend_url"]:
            self.embedding = "nomic-embed-text"
            self.client = OpenAI(base_url=config["backend_url"])
        else:
            self.embedding = "text-embedding-3-small"
            self.client = OpenAI(base_url=config["backend_url"])
        # chromadb 持久化配置
        persist_path = config.get("chroma_persist_path", "./chroma_memory")
        self.chroma_client = chromadb.PersistentClient(path=persist_path)
        if hasattr(self.chroma_client, "get_or_create_collection"):
            self.situation_collection = self.chroma_client.get_or_create_collection(name=name)
        else:
            try:
                self.situation_collection = self.chroma_client.get_collection(name=name)
            except Exception:
                self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """Get embedding for a text, using OpenAI or BigModel client, with安全处理 for zhipuai限制"""
        if self.use_bigmodel:
            MAX_TOKENS = 3072
            MAX_BATCH = 64
            # 简单用字符数近似token数，1 token ≈ 2字符
            def safe_truncate(s):
                return s[:MAX_TOKENS*2] if len(s) > MAX_TOKENS*2 else s

            # 支持单条或多条
            if isinstance(text, str):
                safe_texts = [safe_truncate(text)]
            else:
                safe_texts = [safe_truncate(t) for t in text]

            embeddings = []
            for i in range(0, len(safe_texts), MAX_BATCH):
                batch = safe_texts[i:i+MAX_BATCH]
                resp = self.client.embeddings.create(model=self.embedding, input=batch)
                embeddings.extend([d.embedding for d in resp.data])
            # 兼容原有接口，单条返回一条，多条返回列表
            return embeddings[0] if isinstance(text, str) else embeddings
        else:
            response = self.client.embeddings.create(
                model=self.embedding, input=text
            )
            return response.data[0].embedding

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
