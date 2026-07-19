from learning_runtime.agent.models import AgentCommand, AgentInput, InputKind


COMMANDS = {f"/{command.value}": command for command in AgentCommand}


def parse_agent_input(raw: str) -> AgentInput:
    stripped = raw.strip()
    if not stripped:
        return AgentInput(InputKind.EMPTY, raw)
    if stripped in COMMANDS:
        return AgentInput(InputKind.COMMAND, raw, COMMANDS[stripped])
    if stripped.startswith("/"):
        return AgentInput(InputKind.UNKNOWN_COMMAND, raw)
    return AgentInput(InputKind.MESSAGE, raw)
