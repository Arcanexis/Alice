#!/usr/bin/env python3
"""
Tavily搜索工具 - 为AI模型提供便捷的网络搜索功能
使用方法: python tavily_search.py --query "你的搜索查询"
"""

import os
import json
import argparse
from typing import Optional, List, Dict, Any
from tavily import TavilyClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TavilySearchTool:
    """Tavily搜索工具封装类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Tavily客户端
        
        Args:
            api_key: Tavily API密钥,如果未提供则从环境变量读取
        """
        # 安全性优化：移除硬编码密钥，仅从环境变量或参数读取
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 TAVILY_API_KEY，请在 .env 文件中配置。")
        self.client = TavilyClient(self.api_key)
    
    def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        topic: str = "general",
        days: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """
        执行搜索查询
        """
        try:
            # 构建搜索参数
            search_params = {
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
                "topic": topic,
                "include_answer": include_answer
            }
            
            # 添加可选参数
            if days is not None:
                search_params["days"] = days
            if include_domains:
                search_params["include_domains"] = include_domains
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains
            
            # 执行搜索
            response = self.client.search(**search_params)
            return response
            
        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def quick_search(self, query: str) -> str:
        """
        快速搜索并返回简洁的文本结果 (Markdown 格式)
        """
        response = self.search(query, max_results=3)
        
        if "error" in response:
            return f"搜索出错: {response['error']}"
        
        output = [f"## 搜索查询: {response.get('query', query)}\n"]
        
        # 添加AI生成的答案
        if response.get("answer"):
            output.append(f"> **AI 摘要**: {response['answer']}\n")
        
        # 添加搜索结果
        output.append("### 搜索结果:")
        for i, result in enumerate(response.get("results", []), 1):
            output.append(f"\n{i}. **{result.get('title', '无标题')}**")
            output.append(f"   - URL: {result.get('url', '无链接')}")
            output.append(f"   - 摘要: {result.get('content', '无内容')[:300]}...")
            if result.get('score'):
                output.append(f"   - 相关性: {result['score']:.2f}")
        
        return "\n".join(output)
    
    def deep_research(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        深度研究模式 - 获取更全面的信息
        """
        return self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )
    
    def news_search(self, query: str, days: int = 7, max_results: int = 5) -> Dict[str, Any]:
        """
        新闻搜索模式 - 获取最新新闻
        """
        return self.search(
            query=query,
            topic="news",
            days=days,
            max_results=max_results
        )


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description="Tavily搜索工具 - AI驱动的网络搜索",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  基础搜索 (返回 Markdown):
    python tavily_search.py --query "Python教程"
  
  深度研究 (返回 JSON):
    python tavily_search.py --query "机器学习" --mode research --max-results 10
  
  新闻搜索 (返回 JSON):
    python tavily_search.py --query "AI新闻" --mode news --days 3
  
  JSON输出模式:
    python tavily_search.py --query "区块链" --json
        """
    )
    
    parser.add_argument("--query", "-q", required=True, help="搜索查询")
    parser.add_argument("--mode", "-m", choices=["basic", "research", "news"], 
                       default="basic", help="搜索模式")
    parser.add_argument("--max-results", "-n", type=int, default=5, 
                       help="最大结果数 (1-20)")
    parser.add_argument("--days", "-d", type=int, help="新闻时间范围(天)")
    parser.add_argument("--json", action="store_true", help="强制以JSON格式输出")
    parser.add_argument("--include-domains", nargs="+", help="限制搜索的域名")
    parser.add_argument("--exclude-domains", nargs="+", help="排除的域名")
    parser.add_argument("--api-key", help="Tavily API密钥")
    
    args = parser.parse_args()
    
    try:
        # 创建搜索工具实例
        tool = TavilySearchTool(api_key=args.api_key)
        
        # 根据模式执行搜索
        if args.mode == "research":
            response = tool.deep_research(args.query, max_results=args.max_results)
            print(json.dumps(response, ensure_ascii=False, indent=2))
        elif args.mode == "news":
            days = args.days if args.days else 7
            response = tool.news_search(args.query, days=days, max_results=args.max_results)
            print(json.dumps(response, ensure_ascii=False, indent=2))
        else:
            # 基础模式
            if args.json:
                response = tool.search(
                    query=args.query,
                    max_results=args.max_results,
                    include_domains=args.include_domains,
                    exclude_domains=args.exclude_domains
                )
                print(json.dumps(response, ensure_ascii=False, indent=2))
            else:
                # 默认返回易读的 Markdown 文本，适合 Alice 直接阅读
                print(tool.quick_search(args.query))
                
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
