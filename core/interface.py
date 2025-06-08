from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InterfaceType(Enum):
    WEB = "web"
    API = "api"
    CLI = "cli"
    MOBILE = "mobile"

@dataclass
class InterfaceConfig:
    type: InterfaceType
    theme: str
    language: str
    timezone: str
    features: List[str]

class ElegantInterface:
    def __init__(self):
        self.configs: Dict[str, InterfaceConfig] = {}
        self.handlers: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        
    def register_interface(self, name: str, config: InterfaceConfig):
        self.configs[name] = config
        logger.info(f"Registered interface: {name}")
        
    def register_handler(self, endpoint: str, handler: Callable):
        self.handlers[endpoint] = handler
        logger.info(f"Registered handler for: {endpoint}")
        
    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)
        logger.info("Added middleware")
        
    async def process_request(self, interface: str, endpoint: str, data: Any) -> Any:
        if interface not in self.configs:
            raise ValueError(f"Interface {interface} not found")
            
        if endpoint not in self.handlers:
            raise ValueError(f"Endpoint {endpoint} not found")
            
        try:
            for middleware in self.middleware:
                data = await middleware(data)
                
            result = await self.handlers[endpoint](data)
            return self._format_response(result, self.configs[interface])
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise
            
    def _format_response(self, data: Any, config: InterfaceConfig) -> Any:
        if config.type == InterfaceType.API:
            return self._format_api_response(data)
        elif config.type == InterfaceType.WEB:
            return self._format_web_response(data)
        elif config.type == InterfaceType.CLI:
            return self._format_cli_response(data)
        elif config.type == InterfaceType.MOBILE:
            return self._format_mobile_response(data)
            
    def _format_api_response(self, data: Any) -> Dict:
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    def _format_web_response(self, data: Any) -> Dict:
        return {
            "template": "default",
            "data": data,
            "theme": self.configs["web"].theme
        }
        
    def _format_cli_response(self, data: Any) -> str:
        return json.dumps(data, indent=2)
        
    def _format_mobile_response(self, data: Any) -> Dict:
        return {
            "view": "default",
            "data": data,
            "theme": self.configs["mobile"].theme
        }
        
    def get_interface_config(self, name: str) -> Optional[InterfaceConfig]:
        return self.configs.get(name)
        
    def list_interfaces(self) -> List[str]:
        return list(self.configs.keys())
        
    def list_endpoints(self) -> List[str]:
        return list(self.handlers.keys()) 