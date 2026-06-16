import ast
from pathlib import Path

FORBIDDEN_PORT_IMPORT_PREFIXES = (
    "cq.api",
    "cq.backtest",
    "cq.data",
    "cq.exchanges",
    "cq.execution",
    "cq.monitoring",
    "cq.risk",
    "cq.runtime",
    "cq.storage",
    "cq.strategies",
)


def test_port_modules_do_not_import_implementation_layers() -> None:
    ports_dir = Path("src/cq/ports")

    for path in ports_dir.glob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        imports = imported_modules(tree)

        forbidden = [
            module
            for module in imports
            if any(module.startswith(prefix) for prefix in FORBIDDEN_PORT_IMPORT_PREFIXES)
        ]

        assert forbidden == [], f"{path} imports implementation layers: {forbidden}"


def imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.append(node.module)

    return modules
