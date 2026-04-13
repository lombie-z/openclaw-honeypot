"""JSONL transcript parser for OpenClaw session files.

Parses the JSONL event stream into structured dataclasses suitable for
metric computation.

Confirmed format (from live transcripts):
  - Tool calls:  {"type": "toolCall", "name": "...", "arguments": {...}}
  - Tool results: {"role": "toolResult", "toolCallId": "...", "toolName": "..."}
  - Usage:        message.usage.{input, output, cacheRead, cost.total}
  - Thinking:     {"type": "thinking", "text": "..."}
  - Stop reason:  message.stopReason ("toolUse", "stop", etc.)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict
    timestamp: str


@dataclass
class ToolResult:
    tool_call_id: str
    tool_name: str
    content: str
    is_error: bool
    timestamp: str


@dataclass
class AssistantTurn:
    text: str | None
    thinking: str | None
    tool_calls: list[ToolCall]
    usage: dict
    model: str
    stop_reason: str | None
    timestamp: str


@dataclass
class ParsedTranscript:
    session_id: str
    model: str
    user_messages: list[dict] = field(default_factory=list)
    assistant_turns: list[AssistantTurn] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)

    @property
    def all_tool_calls(self) -> list[ToolCall]:
        """All tool calls across all assistant turns, in order."""
        calls = []
        for turn in self.assistant_turns:
            calls.extend(turn.tool_calls)
        return calls

    @property
    def tool_call_sequence(self) -> list[str]:
        """Ordered list of tool names called during the session."""
        return [tc.name for tc in self.all_tool_calls]

    @property
    def total_input_tokens(self) -> int:
        return sum(t.usage.get("input", 0) for t in self.assistant_turns)

    @property
    def total_output_tokens(self) -> int:
        return sum(t.usage.get("output", 0) for t in self.assistant_turns)

    @property
    def total_cost_usd(self) -> float:
        total = 0.0
        for t in self.assistant_turns:
            cost = t.usage.get("cost", {})
            if isinstance(cost, dict):
                total += cost.get("total", 0.0)
            elif isinstance(cost, (int, float)):
                total += cost
        return total

    @property
    def duration_seconds(self) -> float:
        """Wall-clock duration from first to last event timestamp."""
        timestamps = []
        for msg in self.user_messages:
            if msg.get("timestamp"):
                timestamps.append(msg["timestamp"])
        for turn in self.assistant_turns:
            if turn.timestamp:
                timestamps.append(turn.timestamp)
        for tr in self.tool_results:
            if tr.timestamp:
                timestamps.append(tr.timestamp)

        if len(timestamps) < 2:
            return 0.0

        # Parse ISO timestamps
        from datetime import datetime, timezone

        def parse_ts(ts: str) -> float:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                return dt.timestamp()
            except (ValueError, AttributeError):
                return 0.0

        parsed = [parse_ts(t) for t in timestamps if isinstance(t, str)]
        parsed = [p for p in parsed if p > 0]
        if len(parsed) < 2:
            return 0.0
        return max(parsed) - min(parsed)


def parse_transcript(path: Path) -> ParsedTranscript:
    """Parse a JSONL transcript file into a ParsedTranscript.

    Handles malformed lines gracefully (skips with warning).
    """
    events = []
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # skip malformed lines

    session_id = ""
    model = ""
    user_messages: list[dict] = []
    assistant_turns: list[AssistantTurn] = []
    tool_results: list[ToolResult] = []

    for event in events:
        event_type = event.get("type")
        timestamp = event.get("timestamp", "")

        if event_type == "session":
            session_id = event.get("id", "")

        elif event_type == "model_change":
            model = event.get("modelId", model)

        elif event_type == "message":
            msg = event.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", [])

            if role == "user":
                # Could be a regular user message or a tool result
                if isinstance(content, list):
                    # Check if this is a tool result message
                    has_tool_result = any(
                        isinstance(c, dict) and c.get("type") == "tool_result"
                        for c in content
                    )
                    if has_tool_result:
                        # This is an older format tool result (type: tool_result inside user message)
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_result":
                                tool_results.append(ToolResult(
                                    tool_call_id=block.get("tool_use_id", ""),
                                    tool_name="",
                                    content=_extract_text(block.get("content", "")),
                                    is_error=block.get("is_error", False),
                                    timestamp=timestamp,
                                ))
                    else:
                        text = _extract_text(content)
                        user_messages.append({"text": text, "timestamp": timestamp})
                elif isinstance(content, str):
                    user_messages.append({"text": content, "timestamp": timestamp})

            elif role == "toolResult":
                # OpenClaw native format: role is "toolResult" at the message level
                tool_results.append(ToolResult(
                    tool_call_id=msg.get("toolCallId", ""),
                    tool_name=msg.get("toolName", ""),
                    content=_extract_text(content),
                    is_error=msg.get("isError", False),
                    timestamp=timestamp,
                ))

            elif role == "assistant":
                text_parts = []
                thinking_parts = []
                tool_calls = []
                usage = msg.get("usage", {})
                msg_model = msg.get("model", model)
                stop_reason = msg.get("stopReason")

                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        block_type = block.get("type", "")
                        if block_type == "text":
                            text_parts.append(block.get("text", ""))
                        elif block_type == "thinking":
                            thinking_parts.append(block.get("text", ""))
                        elif block_type == "toolCall":
                            tool_calls.append(ToolCall(
                                id=block.get("id", ""),
                                name=block.get("name", ""),
                                arguments=block.get("arguments", {}),
                                timestamp=timestamp,
                            ))
                        elif block_type == "tool_use":
                            # Alternative format (Anthropic native)
                            tool_calls.append(ToolCall(
                                id=block.get("id", ""),
                                name=block.get("name", ""),
                                arguments=block.get("input", {}),
                                timestamp=timestamp,
                            ))
                elif isinstance(content, str):
                    text_parts.append(content)

                assistant_turns.append(AssistantTurn(
                    text="\n".join(text_parts) if text_parts else None,
                    thinking="\n".join(thinking_parts) if thinking_parts else None,
                    tool_calls=tool_calls,
                    usage=usage,
                    model=msg_model,
                    stop_reason=stop_reason,
                    timestamp=timestamp,
                ))

    return ParsedTranscript(
        session_id=session_id,
        model=model,
        user_messages=user_messages,
        assistant_turns=assistant_turns,
        tool_results=tool_results,
    )


def _extract_text(content) -> str:
    """Extract plain text from various content formats."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(parts)
    return str(content)
