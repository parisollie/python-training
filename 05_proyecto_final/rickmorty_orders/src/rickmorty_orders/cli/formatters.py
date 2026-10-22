"""Formateadores de output del CLI usando rich."""

from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


def print_orders_table(orders: list[dict[str, Any]]) -> None:
    """Imprime una tabla de ordenes."""
    if not orders:
        console.print("[yellow]No hay ordenes.[/yellow]")
        return

    table = Table(title="Ordenes")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Cliente", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Items", justify="right")
    table.add_column("Total", justify="right", style="bold green")

    for order in orders:
        table.add_row(
            str(order.get("id", ""))[:8] + "...",
            str(order.get("customer_email", "")),
            str(order.get("status", "")),
            str(order.get("total_items", 0)),
            f"${order.get('total', 0):.2f}",
        )

    console.print(table)


def print_order_detail(order: dict[str, Any]) -> None:
    """Imprime el detalle de una orden."""
    console.print(f"[bold cyan]Orden:[/bold cyan] {order.get('id')}")
    console.print(f"[bold]Cliente:[/bold] {order.get('customer_email')}")
    console.print(f"[bold]Status:[/bold] {order.get('status')}")
    console.print(f"[bold]Creada:[/bold] {order.get('created_at', 'N/A')}")
    console.print()

    items = order.get("items", [])
    if items:
        table = Table(title="Items")
        table.add_column("Producto")
        table.add_column("Cantidad", justify="right")
        table.add_column("Precio unit.", justify="right")
        table.add_column("Subtotal", justify="right")

        for item in items:
            table.add_row(
                str(item.get("character_name", item.get("product", ""))),
                str(item.get("quantity", 0)),
                f"${item.get('unit_price', 0):.2f}",
                f"${item.get('subtotal', 0):.2f}",
            )
        console.print(table)

    console.print()
    console.print(f"[bold]Subtotal:[/bold] ${order.get('subtotal', 0):.2f}")
    console.print(f"[bold]IVA:[/bold] ${order.get('tax', 0):.2f}")
    total = order.get("total", 0)
    console.print(f"[bold green]Total:[/bold green] [bold green]${total:.2f}[/bold green]")


def success(message: str) -> None:
    """Mensaje de exito."""
    console.print(f"[green]OK[/green] {message}")


def error(message: str) -> None:
    """Mensaje de error."""
    console.print(f"[red]ERROR[/red] {message}", style="red")


def warning(message: str) -> None:
    """Mensaje de advertencia."""
    console.print(f"[yellow]WARN[/yellow] {message}")
