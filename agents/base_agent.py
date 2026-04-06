"""
AI Agent基类
所有专业Agent的抽象基类，定义统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json


class BaseAgent(ABC):
    """AI Agent基类"""
    
    def __init__(self, llm_client, agent_name: str, prompt_template_path: Optional[str] = None):
        """
        初始化Agent
        
        Args:
            llm_client: LLM客户端实例
            agent_name: Agent名称
            prompt_template_path: 提示词模板路径
        """
        self.llm_client = llm_client
        self.agent_name = agent_name
        self.system_prompt = self._load_system_prompt(prompt_template_path)
        self.context: Dict[str, Any] = {}
    
    def _load_system_prompt(self, path: Optional[str]) -> str:
        """加载系统提示词"""
        pass
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """
        构建分析提示词
        
        Args:
            context: 上下文数据
            
        Returns:
            完整的提示词字符串
        """
        pass
    
    def _call_llm(self, prompt: str) -> str:
        """
        调用LLM API
        
        Args:
            prompt: 提示词
            
        Returns:
            LLM响应文本
        """
        pass
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应为结构化数据
        
        Args:
            response: LLM响应文本
            
        Returns:
            解析后的字典
        """
        pass
    
    @abstractmethod
    def get_focus_areas(self) -> List[str]:
        """
        获取Agent的关注领域
        
        Returns:
            关注领域列表
        """
        pass
    
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行分析
        
        Args:
            context: 上下文数据
            
        Returns:
            分析结果字典
        """
        pass