import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VECTOR_STORE_PATH = PROJECT_ROOT / "memory" / "vector_store"

print("1. 开始导入 chromadb...")
import chromadb
print("   ✓ chromadb 导入成功")

print("\n2. 创建 PersistentClient...")
client = chromadb.PersistentClient(path=str(VECTOR_STORE_PATH))
print("   ✓ Client 创建成功")

print("\n3. 获取或创建 collection...")
collection = client.get_or_create_collection(name="chat_memory")
print("   ✓ Collection 创建成功")

print("\n4. 准备测试数据...")
test_vector = [0.1] * 768  # 模拟 768 维向量
print(f"   ✓ 向量准备完成，长度: {len(test_vector)}")

print("\n5. 执行 collection.add() 写入...")
print("   (如果卡在这里，就是写入操作的问题)")
collection.add(
    ids=["test_001"],
    embeddings=[test_vector],
    documents=["测试文本"]
)
print("   ✓ 写入成功！")

print("\n6. 执行查询测试...")
result = collection.query(query_embeddings=[test_vector], n_results=1)
print(f"   ✓ 查询成功，结果: {result['documents']}")

print("\n🎉 全部测试通过！")
