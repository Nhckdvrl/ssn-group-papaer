"""Local implementation of upstream single-tool cognition calls.

Preserves component messages, schemas, token budgets and temperatures.
Never constructs a hosted provider; action calls use the existing adapter.
"""
import copy
import hashlib
import json
import time

from native_tool_loop import ToolClient, template_messages


class LocalComponentClient(ToolClient):
    def __init__(self, base, max_calls, role):
        super().__init__(base)
        self.max_calls = max_calls
        self.context = {"role": role}

    def _budget(self):
        if len(self.base.calls) >= self.max_calls:
            raise RuntimeError("Local model call budget exhausted")

    def call_tools(self, *args, **kwargs):
        self._budget()
        return super().call_tools(*args, **kwargs)

    def chat(self, messages, max_tokens=128, temperature=.7):
        self._budget()
        return self.base.chat(template_messages(messages), max_tokens=max_tokens,
                              temperature=temperature, kind=self.context.get("role", "chat"))

    def call_tool(self, messages, tool, max_tokens=128, temperature=0.0):
        from vllm import SamplingParams
        from vllm.sampling_params import StructuredOutputsParams

        self._budget()
        normalized = template_messages(messages)
        normalized[0]["content"] += (
            "\nUse the provided tool " + tool["name"] + ": " + tool.get("description", "")
            + ". Return only its JSON arguments matching the schema: "
            + json.dumps(tool["parameters"], ensure_ascii=False))
        prompt = self.base.tokenizer.apply_chat_template(
            normalized, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        start = time.monotonic()
        result = self.base.llm.generate([prompt], SamplingParams(
            max_tokens=max_tokens, temperature=temperature,
            seed=self.base.seed + len(self.base.calls),
            structured_outputs=StructuredOutputsParams(json=tool["parameters"])),
            use_tqdm=False)[0]
        completion = result.outputs[0]
        try:
            parsed, error = json.loads(completion.text), None
        except Exception as exc:
            parsed, error = None, f"{type(exc).__name__}: {exc}"
        row = {
            "id": len(self.base.calls), "kind": "native_single_tool",
            "context": copy.deepcopy(self.context), "tool": copy.deepcopy(tool),
            "messages": copy.deepcopy(messages), "template_messages": normalized,
            "seed": self.base.seed + len(self.base.calls), "temperature": temperature,
            "max_tokens": max_tokens, "response": completion.text, "parsed": parsed,
            "parse_error": error, "finish_reason": completion.finish_reason,
            "prompt_tokens": len(result.prompt_token_ids),
            "completion_tokens": len(completion.token_ids),
            "wall_seconds": time.monotonic() - start,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
        self.base.calls.append(row)
        with self.base.trace_file.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return parsed
