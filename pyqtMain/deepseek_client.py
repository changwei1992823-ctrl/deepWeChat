import os
import requests

try:
    import deepseek
    HAS_DEEPSEEK = True
except Exception:
    deepseek = None
    HAS_DEEPSEEK = False


class DeepSeekClient:
    def __init__(self, api_key: str = None):
        self.api_key = (api_key or "").strip() or None
        self.api_base = os.environ.get("DEEPSEEK_API_BASE")

    def _extract_deepseek_response(self, response):
        if isinstance(response, dict):
            if "results" in response:
                return response.get("results") or []
            if "choices" in response:
                results = []
                for c in response.get("choices") or []:
                    msg = c.get("message") or {}
                    text = msg.get("content") if isinstance(msg, dict) else None
                    if not text:
                        text = c.get("text")
                    if text:
                        results.append(text)
                return results
        if isinstance(response, str):
            return [response]
        if isinstance(response, list):
            return response
        return [str(response)]

    def _try_call_deepseek(self, query: str, limit: int = 10):
        if not HAS_DEEPSEEK or deepseek is None:
            raise RuntimeError("deepseek 库未安装")

        if hasattr(deepseek, "search") and callable(getattr(deepseek, "search")):
            return deepseek.search(query, limit=limit)

        for api_obj in (getattr(deepseek, "DeepSeekAPI", None), getattr(getattr(deepseek, "api", None), "DeepSeekAPI", None)):
            if api_obj and callable(api_obj):
                try:
                    inst = api_obj(self.api_key) if self.api_key is not None else api_obj()
                    if hasattr(inst, "chat_completion") and callable(getattr(inst, "chat_completion")):
                        response = inst.chat_completion(prompt=query, stream=False)
                        results = self._extract_deepseek_response(response)
                        if results:
                            return results[:limit]
                except Exception:
                    pass

        client_classes = [name for name in dir(deepseek) if name.lower().startswith("client") or "deepseek" in name.lower()]
        for cls_name in client_classes:
            cls = getattr(deepseek, cls_name)
            try:
                if callable(cls):
                    try:
                        inst = cls(self.api_key) if self.api_key is not None else cls()
                    except Exception:
                        inst = cls()
                    if hasattr(inst, "search") and callable(getattr(inst, "search")):
                        return inst.search(query, limit=limit)
            except Exception:
                continue

        for name in dir(deepseek):
            if any(k in name.lower() for k in ("search", "query", "find")):
                attr = getattr(deepseek, name)
                if callable(attr):
                    try:
                        return attr(query, limit=limit)
                    except Exception:
                        try:
                            return attr(query)
                        except Exception:
                            continue

        raise RuntimeError("无法识别的 deepseek SDK 接口，无法调用搜索方法")

    def search(self, query: str, limit: int = 10):
        if not query:
            return []

        if HAS_DEEPSEEK:
            try:
                return self._try_call_deepseek(query, limit=limit)
            except Exception as e:
                print(f"deepseek 库调用失败: {e}")

        if self.api_key and self.api_base:
            try:
                url = self.api_base.rstrip("/") + "/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-v4-flash",
                    "messages": [{"role": "user", "content": query}],
                    "stream": False
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, dict) and "choices" in data:
                    choices = data.get("choices") or []
                    results = []
                    for c in choices:
                        msg = c.get("message") or {}
                        text = msg.get("content") if isinstance(msg, dict) else None
                        if not text:
                            text = c.get("text")
                        if text:
                            results.append(text)
                    if results:
                        return results
                if isinstance(data, dict) and "results" in data:
                    return data.get("results") or []
                return [str(data)]
            except Exception as e:
                warning = f"通过 HTTP API 调用 DeepSeek 失败: {e}"
                print(warning)
                return {"results": [f"模拟结果：{query} - {i+1}" for i in range(min(limit, 5))], "warning": warning}

        return {"results": [f"模拟结果：{query} - {i+1}" for i in range(min(limit, 5))], "warning": "未配置 HTTP API 基础地址，使用模拟数据。"}
