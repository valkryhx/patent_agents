#!/usr/bin/env python3
"""
Test script for Description Generation Logic
Tests the automatic description generation from topic
"""

def extract_tech_keywords(topic: str) -> list:
    """Extract technical keywords from topic"""
    keywords = []
    
    # 技术领域关键词
    tech_domains = {
        "人工智能": ["AI", "机器学习", "深度学习", "神经网络", "算法"],
        "区块链": ["分布式账本", "智能合约", "加密", "共识机制", "去中心化"],
        "物联网": ["传感器", "连接", "数据采集", "远程控制", "自动化"],
        "云计算": ["虚拟化", "分布式", "弹性扩展", "服务化", "资源管理"],
        "大数据": ["数据分析", "存储", "处理", "挖掘", "可视化"],
        "5G": ["通信", "网络", "低延迟", "高带宽", "连接密度"],
        "量子计算": ["量子比特", "叠加态", "纠缠", "量子算法", "量子优势"],
        "生物技术": ["基因", "蛋白质", "细胞", "生物信息", "合成生物学"],
        "新能源": ["太阳能", "风能", "储能", "氢能", "核能"],
        "新材料": ["纳米材料", "复合材料", "智能材料", "生物材料", "超导材料"]
    }
    
    # 技术类型关键词
    tech_types = {
        "系统": ["架构", "模块", "接口", "集成", "优化"],
        "方法": ["算法", "流程", "步骤", "策略", "机制"],
        "装置": ["设备", "仪器", "工具", "组件", "结构"],
        "技术": ["工艺", "配方", "参数", "条件", "标准"]
    }
    
    # 从topic中识别技术领域
    topic_lower = topic.lower()
    for domain, domain_keywords in tech_domains.items():
        if domain in topic_lower:
            keywords.extend(domain_keywords[:3])  # 取前3个关键词
    
    # 从topic中识别技术类型
    for tech_type, type_keywords in tech_types.items():
        if tech_type in topic_lower:
            keywords.extend(type_keywords[:2])  # 取前2个关键词
    
    # 如果没有识别到特定领域，添加通用技术关键词
    if not keywords:
        keywords = ["技术创新", "系统优化", "方法改进", "性能提升", "应用扩展"]
    
    return keywords

def generate_tech_description(topic: str, keywords: list) -> str:
    """Generate technical description based on topic and keywords"""
    try:
        # 构建技术描述模板
        description_template = f"""一种基于{', '.join(keywords[:3])}的{topic}技术方案，该方案通过创新的技术手段解决了现有技术中存在的问题。

主要技术特点包括：
1. 采用{keywords[0] if keywords else '先进'}技术，提高系统性能和可靠性
2. 运用{keywords[1] if len(keywords) > 1 else '创新'}方法，优化处理流程和效率
3. 结合{keywords[2] if len(keywords) > 2 else '现代'}技术，增强系统的适应性和扩展性

技术优势：
- 相比传统方案，具有更高的{keywords[0] if keywords else '技术'}水平
- 通过{keywords[1] if len(keywords) > 1 else '创新'}设计，实现更好的用户体验
- 采用{keywords[2] if len(keywords) > 2 else '先进'}架构，确保系统的稳定性和可维护性

应用领域：
该技术可广泛应用于相关行业，为{keywords[0] if keywords else '技术'}发展提供新的解决方案，具有重要的实用价值和市场前景。"""
        
        return description_template
        
    except Exception as e:
        print(f"Error generating tech description: {e}")
        # 返回基础描述
        return f"一种基于{topic}的技术创新方案，通过先进的技术手段解决现有问题，具有重要的实用价值和市场前景。"

def test_description_generation():
    """Test the description generation functionality"""
    print("🧪 Testing Description Generation Logic")
    print("=" * 50)
    
    # Test topics
    test_topics = [
        "量子计算",
        "区块链技术",
        "人工智能系统",
        "物联网平台",
        "云计算架构",
        "大数据分析",
        "5G通信网络",
        "生物技术应用",
        "新能源系统",
        "新材料技术"
    ]
    
    for topic in test_topics:
        print(f"\n🔍 Testing topic: {topic}")
        print("-" * 30)
        
        try:
            # Extract keywords
            keywords = extract_tech_keywords(topic)
            print(f"   📝 Extracted keywords: {keywords}")
            
            # Generate description
            description = generate_tech_description(topic, keywords)
            
            if description:
                print(f"✅ Generated description ({len(description)} chars):")
                print(f"   {description[:200]}...")
            else:
                print(f"❌ Failed to generate description")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n✅ Description generation test completed!")

def test_specific_topic():
    """Test a specific topic in detail"""
    import sys
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        print(f"\n🔍 Detailed test for topic: {topic}")
        print("=" * 50)
        
        try:
            # Extract keywords
            keywords = extract_tech_keywords(topic)
            print(f"📝 Extracted keywords: {keywords}")
            
            # Generate description
            description = generate_tech_description(topic, keywords)
            print(f"\n🔧 Generated description:")
            print(f"   {description}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Main test function"""
    import sys
    if len(sys.argv) > 1:
        test_specific_topic()
    else:
        test_description_generation()

if __name__ == "__main__":
    main()