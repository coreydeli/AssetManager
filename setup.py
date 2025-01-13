from setuptools import setup, find_packages

setup(
    name="asset-manager",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "alembic",
        "asyncpg",
        "pydantic-settings"
    ],
)