#!/usr/bin/env python3
"""
智能体系统配置文件
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.default_config = {
            "glm": {
                "api_key": "",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": "glm-4.5-flash",
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout": 60
            },
            "mcp_server": {
                "name": "agentic-mcp-server",
                "version": "1.0.0",
                "log_level": "INFO"
            },
            "agent": {
                "planning_timeout": 30,
                "execution_timeout": 300,
                "max_retries": 3,
                "retry_delay": 1
            },
            "tools": {
                "data_collector": {
                    "enabled": True,
                    "timeout": 60,
                    "max_data_points": 10000
                },
                "data_analyzer": {
                    "enabled": True,
                    "timeout": 120,
                    "supported_analysis_types": [
                        "descriptive", "exploratory", "statistical", "ml_prediction"
                    ]
                },
                "report_generator": {
                    "enabled": True,
                    "timeout": 90,
                    "supported_formats": ["markdown", "html", "pdf", "json"],
                    "default_format": "markdown"
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "agentic.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "ui": {
                "theme": "default",
                "language": "zh_CN",
                "auto_save": True,
                "show_progress": True
            }
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return self._merge_configs(self.default_config, user_config)
            except Exception as e:
                print(f"配置文件加载失败: {e}，使用默认配置")
                return self.default_config.copy()
        else:
            # 创建默认配置文件
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"配置文件保存失败: {e}")
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """合并默认配置和用户配置"""
        result = default.copy()
        
        def merge_dict(d1: Dict[str, Any], d2: Dict[str, Any]):
            for key, value in d2.items():
                if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
                    merge_dict(d1[key], value)
                else:
                    d1[key] = value
        
        merge_dict(result, user)
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到父级配置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存配置
        self.save_config(self.config)
    
    def get_glm_config(self) -> Dict[str, Any]:
        """获取GLM配置"""
        return self.get('glm', {})
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """获取MCP服务器配置"""
        return self.get('mcp_server', {})
    
    def get_agent_config(self) -> Dict[str, Any]:
        """获取智能体配置"""
        return self.get('agent', {})
    
    def get_tools_config(self) -> Dict[str, Any]:
        """获取工具配置"""
        return self.get('tools', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return self.get('ui', {})
    
    def update_glm_api_key(self, api_key: str):
        """更新GLM API密钥"""
        self.set('glm.api_key', api_key)
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """检查工具是否启用"""
        return self.get(f'tools.{tool_name}.enabled', True)
    
    def get_tool_timeout(self, tool_name: str) -> int:
        """获取工具超时时间"""
        return self.get(f'tools.{tool_name}.timeout', 60)
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        try:
            # 检查必需的配置项
            required_keys = [
                'glm.api_key',
                'glm.base_url',
                'glm.model'
            ]
            
            for key in required_keys:
                if not self.get(key):
                    print(f"配置验证失败: 缺少必需的配置项 {key}")
                    return False
            
            # 检查工具配置
            tools_config = self.get_tools_config()
            for tool_name, tool_config in tools_config.items():
                if not isinstance(tool_config, dict):
                    continue
                    
                if tool_config.get('enabled', True):
                    timeout = tool_config.get('timeout', 60)
                    if timeout <= 0:
                        print(f"配置验证失败: 工具 {tool_name} 的超时时间必须大于0")
                        return False
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False
    
    def print_config(self):
        """打印当前配置"""
        import json
        print("当前配置:")
        print(json.dumps(self.config, ensure_ascii=False, indent=2))

# 全局配置实例
config = Config()

def get_config() -> Config:
    """获取全局配置实例"""
    return config

def get_glm_api_key() -> Optional[str]:
    """获取GLM API密钥"""
    # 优先级: 环境变量 > 配置文件 > .private文件
    api_key = os.getenv("GLM_API_KEY")
    if api_key:
        return api_key
    
    api_key = config.get('glm.api_key')
    if api_key:
        return api_key
    
    # 尝试从.private目录读取
    private_key_file = Path("../.private/GLM_API_KEY")
    if private_key_file.exists():
        api_key = private_key_file.read_text().strip()
        if api_key:
            # 更新配置文件
            config.update_glm_api_key(api_key)
            return api_key
    
    return None

def get_glm_base_url() -> str:
    """获取GLM基础URL"""
    return config.get('glm.base_url', 'https://open.bigmodel.cn/api/paas/v4')

def get_glm_model() -> str:
    """获取GLM模型名称"""
    return config.get('glm.model', 'glm-4.5-flash')

def get_glm_temperature() -> float:
    """获取GLM温度参数"""
    return config.get('glm.temperature', 0.7)

def get_glm_max_tokens() -> int:
    """获取GLM最大token数"""
    return config.get('glm.max_tokens', 4000)

def get_glm_timeout() -> int:
    """获取GLM超时时间"""
    return config.get('glm.timeout', 60)

def get_mcp_server_name() -> str:
    """获取MCP服务器名称"""
    return config.get('mcp_server.name', 'agentic-mcp-server')

def get_mcp_server_version() -> str:
    """获取MCP服务器版本"""
    return config.get('mcp_server.version', '1.0.0')

def get_log_level() -> str:
    """获取日志级别"""
    return config.get('logging.level', 'INFO')

def get_log_file() -> str:
    """获取日志文件路径"""
    return config.get('logging.file', 'agentic.log')

def is_tool_enabled(tool_name: str) -> bool:
    """检查工具是否启用"""
    return config.is_tool_enabled(tool_name)

def get_tool_timeout(tool_name: str) -> int:
    """获取工具超时时间"""
    return config.get_tool_timeout(tool_name)

if __name__ == "__main__":
    # 测试配置
    print("配置测试:")
    print(f"GLM API Key: {'已设置' if get_glm_api_key() else '未设置'}")
    print(f"GLM Base URL: {get_glm_base_url()}")
    print(f"GLM Model: {get_glm_model()}")
    print(f"MCP Server: {get_mcp_server_name()} v{get_mcp_server_version()}")
    print(f"Log Level: {get_log_level()}")
    
    print("\n工具状态:")
    tools = ['data_collector', 'data_analyzer', 'report_generator']
    for tool in tools:
        enabled = is_tool_enabled(tool)
        timeout = get_tool_timeout(tool)
        print(f"  {tool}: {'✅' if enabled else '❌'} (超时: {timeout}s)")
    
    print(f"\n配置验证: {'✅ 通过' if config.validate_config() else '❌ 失败'}")