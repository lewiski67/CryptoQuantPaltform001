import ast
from pathlib import Path

FORBIDDEN_FEATURE_IMPORT_PREFIXES = (
    "cq.api",
    "cq.backtest",
    "cq.exchanges",
    "cq.execution",
    "cq.monitoring",
    "cq.risk",
    "cq.runtime",
    "cq.storage",
    "cq.strategies",
)


def test_feature_modules_do_not_import_runtime_or_implementation_layers() -> None:
    feature_dir = Path("src/cq/features")

    for path in feature_dir.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        imports = imported_modules(tree)

        forbidden = [
            module
            for module in imports
            if any(module.startswith(prefix) for prefix in FORBIDDEN_FEATURE_IMPORT_PREFIXES)
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
