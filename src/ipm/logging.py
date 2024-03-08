from typing import Optional
from rich.console import Console
from rich.prompt import Confirm, Prompt
from .typing import List, Any

console = Console()
status = console.status("")


def update(message: str, echo: bool = False) -> None:
    return status.update(message) if echo else status.stop()


def info(message: str, echo: bool = False) -> None:
    return console.print(message) if echo else None


def success(message: str, echo: bool = False) -> None:
    return (
        console.print("  [green]:heavy_check_mark:[/green]", str(message))
        if echo
        else None
    )


def warning(message: str, echo: bool = False) -> None:
    return console.print("  [yellow]:warning:[/yellow]", str(message)) if echo else None


def error(message: str, echo: bool = False) -> None:
    return (
        console.print("  [red]:heavy_multiplication_x:[/red]", str(message))
        if echo
        else None
    )


def critical(message: str, echo: bool = False) -> None:
    return (
        console.print("".join((" [bold red]", str(message), "[/bold red]")))
        if echo
        else None
    )


def tada(message: str = "工作完成!", echo: bool = True) -> None:
    return console.print("\n[red]:tada:[/red]", str(message), "\n") if echo else None


def confirm(message: str, default: bool = False) -> bool:
    return Confirm.ask(str(message), default=default)


def ask(
    message: str,
    choices: Optional[List[str]] = None,
    default: Any = None,
    echo: bool = False,
) -> Any:
    return Prompt.ask(message, choices=choices, default=default) if echo else default
