import pytest
from core.interface import InterfaceType, InterfaceConfig

def test_interface_registration(elegant_interface):
    config = InterfaceConfig(
        type=InterfaceType.API,
        theme="dark",
        language="en",
        timezone="UTC",
        features=["auth"]
    )
    elegant_interface.register_interface("api", config)
    assert "api" in elegant_interface.configs
    assert elegant_interface.configs["api"].type == InterfaceType.API

async def test_request_processing(elegant_interface):
    async def test_handler(data):
        return {"message": "success"}
        
    elegant_interface.register_handler("/test", test_handler)
    
    result = await elegant_interface.process_request("web", "/test", {})
    assert result["template"] == "default"
    assert result["data"]["message"] == "success"
    assert result["theme"] == "light"

async def test_middleware_chain(elegant_interface):
    middleware_calls = []
    
    async def middleware1(data):
        middleware_calls.append(1)
        return {"step": 1, **data}
        
    async def middleware2(data):
        middleware_calls.append(2)
        return {"step": 2, **data}
        
    async def test_handler(data):
        return data
        
    elegant_interface.add_middleware(middleware1)
    elegant_interface.add_middleware(middleware2)
    elegant_interface.register_handler("/test", test_handler)
    
    result = await elegant_interface.process_request("web", "/test", {"initial": True})
    assert middleware_calls == [1, 2]
    assert result["data"]["step"] == 2
    assert result["data"]["initial"] is True

def test_interface_config_retrieval(elegant_interface):
    config = elegant_interface.get_interface_config("web")
    assert config is not None
    assert config.type == InterfaceType.WEB
    assert config.theme == "light"
    
    assert elegant_interface.get_interface_config("nonexistent") is None 