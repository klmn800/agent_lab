
Rotation cadence: review opportunistically when a session's `ls outbox/` shows a large file. No fixed schedule.

## When to use the outbox vs another channel

- **Outbox (`outbox/for_<agent>.md`)** — ongoing, threaded conversation with another agent. Use when you expect a back-and-forth, or when the message needs to land at the recipient's next session-start hook.
- **Recipient's `inbox/`** — one-off drops from developer/dev sessions. You can't write here directly (write guard blocks); for inter-agent communication, the outbox IS the right channel.
- **`reference/staging/`** — TA can write to `reference/` directly (5/17 read-only restriction lifted 5/18 PM). The staging gate remains available for pattern claims about market behavior that need validation rigor before becoming reference: notice in morning session → outbox to MA → MA stages → Ben graduates.
- **`notes_for_ben.md`** — direct to Ben. Not for inter-agent traffic.
