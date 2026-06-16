import ast
from pathlib import Path

FORBIDDEN_STORAGE_IMPORT_PREFIXES = (
    "cq.api",
    "cq.backtest",
    "cq.exchanges",
    "cq.execution",
    "cq.monitoring",
    "cq.risk",
    "cq.runtime",
    "cq.strategies",
)


def test_storage_modules_do_not_import_runtime_or_implementation_layers() -> None:
    storage_dir = Path("src/cq/storage")

    for path in storage_dir.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        imports = imported_modules(tree)

        forbidden = [
            module
            for module in imports
            if any(module.startswith(prefix) for prefix in FORBIDDEN_STORAGE_IMPORT_PREFIXES)
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
