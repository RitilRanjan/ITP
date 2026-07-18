from typing import Callable, Dict, Any, List

class CommandRegistry:
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, category: str = "General", help_text: str = "", aliases: List[str] = None):
        if aliases is None:
            aliases = []
            
        def decorator(func: Callable):
            self.handlers[name] = func
            self.metadata[name] = {
                "category": category,
                "help": help_text,
                "aliases": aliases
            }
            for alias in aliases:
                self.aliases[alias] = name
                self.handlers[alias] = func
            return func
        return decorator

    def dispatch(self, cmd: str, env: Any, args_str: str, **kwargs) -> Any:
        handler = self.handlers.get(cmd)
        if handler:
            import inspect
            sig = inspect.signature(handler)
            filtered_kwargs = {}
            if 'cmd' in sig.parameters:
                filtered_kwargs['cmd'] = cmd
            for k, v in kwargs.items():
                if k in sig.parameters:
                    filtered_kwargs[k] = v
            return handler(env, args_str, **filtered_kwargs)
        else:
            return None

    def is_registered(self, cmd: str) -> bool:
        return cmd in self.handlers

registry = CommandRegistry()
