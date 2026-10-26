"""Arregla los imports absolutos que genera protoc en los stubs de gRPC.

protoc genera:

    import orders_pb2 as orders__pb2

Pero nuestro paquete vive en `rickmorty_orders.grpc`, asi que el import
correcto es:

    from rickmorty_orders.grpc import orders_pb2 as orders__pb2

Este script es idempotente: si ya esta arreglado, no hace nada.
Se ejecuta SIEMPRE despues de regenerar los stubs con protoc.
"""

from pathlib import Path

GRPC_DIR = Path(__file__).parent / "src" / "rickmorty_orders" / "grpc"
STUB_FILES = ["orders_pb2.py", "orders_pb2_grpc.py"]

OLD = "import orders_pb2 as orders__pb2"
NEW = "from rickmorty_orders.grpc import orders_pb2 as orders__pb2"


def fix_file(path: Path) -> bool:
    """Reescribe el import si esta en la forma vieja. Devuelve True si cambio."""
    content = path.read_text(encoding="utf-8")
    if OLD not in content:
        return False
    path.write_text(content.replace(OLD, NEW), encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for name in STUB_FILES:
        path = GRPC_DIR / name
        if not path.exists():
            print(f"[skip] {name} no existe")
            continue
        if fix_file(path):
            print(f"[fix]  {name}")
            changed += 1
        else:
            print(f"[ok]   {name} (sin cambios)")

    if changed:
        print(f"\n{changed} archivo(s) arreglado(s).")
    else:
        print("\nNada que arreglar.")


if __name__ == "__main__":
    main()
