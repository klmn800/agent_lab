"""
Stop hook: scan the assistant's work since the last user prompt for
unfulfilled "I'll write X" / "I'll log X" / "let me note X" commitments.

If a commitment phrase appears in an assistant text message and NO tool_use
event follows it (in any later assistant message in this same stop window),
return a `block` decision telling TA to either fulfill the commitment or
explicitly cancel it before exiting.

Reads from stdin (Claude Code Stop hook payload):
    {"transcript_path": "...", "session_id": "...", "stop_hook_active": bool}

Test mode:
    python check_commitments.py --test-transcript path/to/fixture.jsonl
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Commitment trigger pattern. Verbs scoped to writing/recording actions
# (not "I'll write the SQL" — but "write" is included anyway because the
# fulfillment check accepts any tool_use as satisfying, so a Bash call
# clears it). False positives self-cancel via TA writing "Cancelling
# commitment to X" in their response.
COMMITMENT_RE = re.compile(
    r"\b(?:i'?ll|i\s+will|let\s+me)\s+"
    r"(?:write|log|note|file|drop|fold|set\s+up|add\s+(?:this\s+|that\s+)?to|"
    r"record|capture|jot|save)\b",
    re.IGNORECASE,
)

# Cancellation escape valve. If this phrase appears anywhere in the assistant
# text after a commitment, treat the commitment as cancelled (not unfulfilled).
CANCEL_RE = re.compile(
    r"\bcancel(?:ling|led)?\s+(?:the\s+)?commitment\b",
    re.IGNORECASE,
)


def iter_events_since_last_user(transcript_path):
    """Walk the JSONL, return events in order from AFTER the last user message.

    Each yielded event is one of:
        ('text', text_str)
        ('tool_use', tool_name)

    Thinking blocks, system messages, attachments, and file-history-snapshots
    are skipped. Only assistant content matters for this check.
    """
    lines = []
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    lines.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except (OSError, IOError):
        return []

    # Find the index of the last real user message (not a system caveat
    # wrapped as user, not an attachment, not a /command meta).
    last_user_idx = -1
    for i, obj in enumerate(lines):
        if obj.get('type') != 'user':
            continue
        msg = obj.get('message') or {}
        content = msg.get('content', '')
        if not isinstance(content, str):
            continue
        # Skip command meta, system reminders, and tool_result wrappers
        if content.startswith('<command-name>') or content.startswith('<local-command-'):
            continue
        if obj.get('isMeta'):
            continue
        last_user_idx = i

    if last_user_idx < 0:
        # No user message found; scan the whole transcript
        last_user_idx = -1

    events = []
    for obj in lines[last_user_idx + 1:]:
        if obj.get('type') != 'assistant':
            continue
        msg = obj.get('message') or {}
        content = msg.get('content')
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict):
                continue
            t = item.get('type')
            if t == 'text':
                events.append(('text', item.get('text', '')))
            elif t == 'tool_use':
                events.append(('tool_use', item.get('name', '')))
            # 'thinking' and others ignored
    return events


def find_unfulfilled_commitments(events):
    """Given the event stream, return a list of unfulfilled commitment snippets.

    A commitment is fulfilled if ANY tool_use event follows it in the stream.
    A commitment is cancelled if a CANCEL_RE match follows it before stop.
    """
    unfulfilled = []
    for i, (kind, payload) in enumerate(events):
        if kind != 'text':
            continue
        text = payload
        if not text:
            continue
        # Find all commitment matches in this text item
        for m in COMMITMENT_RE.finditer(text):
            start = m.start()
            # Grab a short snippet around the match for the report
            snippet_start = max(0, start - 5)
            snippet_end = min(len(text), start + 60)
            snippet = text[snippet_start:snippet_end].replace('\n', ' ').strip()

            # Check for cancellation in same text item AFTER this match
            tail = text[m.end():]
            if CANCEL_RE.search(tail):
                continue

            # Check subsequent events for fulfillment or cancellation
            fulfilled = False
            cancelled = False
            for later_kind, later_payload in events[i + 1:]:
                if later_kind == 'tool_use':
                    fulfilled = True
                    break
                if later_kind == 'text' and CANCEL_RE.search(later_payload or ''):
                    cancelled = True
                    break
            if fulfilled or cancelled:
                continue
            unfulfilled.append(snippet)
    return unfulfilled


def build_block_reason(unfulfilled):
    lines = [
        '<system-reminder>',
        'UNFULFILLED COMMITMENT(S) detected since the last user prompt:',
        '',
    ]
    for snip in unfulfilled[:5]:
        lines.append(f'  - "...{snip}..."')
    if len(unfulfilled) > 5:
        lines.append(f'  - (+{len(unfulfilled) - 5} more)')
    lines.extend([
        '',
        'You committed in your message but no tool call (Write/Edit/Bash/'
        'anything) followed. Either:',
        '  1. Fulfill the commitment now — write the file, run the command, '
        'whatever you said you would do.',
        '  2. Explicitly cancel by writing "Cancelling commitment to X" in '
        'your next message.',
        '',
        'Do not exit the session leaving deferred promises. The deferred '
        'promise IS the bug (see CLAUDE.md inline-write rule).',
        '</system-reminder>',
    ])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--test-transcript',
        type=str,
        help='Path to a fixture JSONL transcript for offline testing.',
    )
    args = parser.parse_args()

    if args.test_transcript:
        transcript_path = args.test_transcript
        stop_hook_active = False
    else:
        try:
            payload = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            # Bad/missing stdin — fail silent rather than block the user
            return
        transcript_path = payload.get('transcript_path')
        stop_hook_active = bool(payload.get('stop_hook_active', False))

    # Already blocked once this stop cycle — let TA actually stop now
    if stop_hook_active:
        return

    if not transcript_path or not Path(transcript_path).exists():
        return

    events = iter_events_since_last_user(transcript_path)
    if not events:
        return

    unfulfilled = find_unfulfilled_commitments(events)
    if not unfulfilled:
        return

    response = {
        'decision': 'block',
        'reason': build_block_reason(unfulfilled),
    }
    json.dump(response, sys.stdout)


if __name__ == '__main__':
    main()
