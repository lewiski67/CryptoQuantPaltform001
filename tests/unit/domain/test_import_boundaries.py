import ast
from pathlib import Path

FORBIDDEN_DOMAIN_IMPORT_PREFIXES = (
    "cq.api",
    "cq.backtest",
    "cq.data",
    "cq.exchanges",
    "cq.execution",
    "cq.monitoring",
    "cq.ports",
    "cq.risk",
    "cq.runtime",
    "cq.storage",
    "cq.strategies",
)


def test_domain_modules_do_not_import_outer_layers() -> None:
    domain_dir = Path("src/cq/domain")

    for path in domain_dir.glob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        imports = imported_modules(tree)

        forbidden = [
            module
            for module in imports
            if any(module.startswith(prefix) for prefix in FORBIDDEN_DOMAIN_IMPORT_PREFIXES)
        ]

        assert forbidden == [], f"{path} imports outer layers: {forbidden}"


def imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.append(node.module)

    return modules
