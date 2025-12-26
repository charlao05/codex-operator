# Release Checklist

Passos recomendados para publicar uma release do `codex-operator`.

1. Atualize a versão em `pyproject.toml` (ex: `0.1.0` → `0.1.1`).
2. Garanta que todos os testes passam localmente:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

3. Rode pre-commit hooks:

```powershell
pre-commit run --all-files
```

4. Gere artefatos (wheel + sdist):

```powershell
pip install --upgrade build
python -m build
```

5. (Opcional) Construa e teste a imagem Docker local:

```powershell
docker build -t codex-operator:local .
docker run --rm -it codex-operator:local
```

6. Tag e push:

```powershell
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin --tags
git push origin hardening/datetime-detect-secrets
```

7. Criar PR no GitHub e preencher descrição com as mudanças (timezone, detect-secrets, CI, packaging, Docker).

8. Após merge na `main`:

- Criar release no GitHub (usar o tag criado).
- Publicar wheel no PyPI (via `twine`) ou usar GitHub Packages.
- Push e publicar imagem Docker no registry desejado.

Exemplo para PyPI (assumindo `~/.pypirc` configurado):

```powershell
pip install --upgrade twine
python -m twine upload dist/*
```

Exemplo para Docker Hub:

```powershell
docker tag codex-operator:local youruser/codex-operator:1.0.0
docker push youruser/codex-operator:1.0.0
```
