# Contributing

1. Open an issue describing the user-visible outcome and acceptance criteria.
2. Create a focused branch from `main`.
3. Add tests for observable behavior and update affected documentation.
4. Run `ruff check .`, `pytest`, and `docker compose config --quiet`.
5. Open a pull request that states what is demonstrated, what remains simulated, and any known limitations.

Never commit credentials, local `.env` files, database volumes, or trained binary artifacts.
