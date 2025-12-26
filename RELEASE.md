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

## Configurar publicação automática (GitHub Actions)

Para habilitar publicação automática quando uma release for criada, adicione os seguintes secrets no repositório (`Settings` → `Secrets and variables` → `Actions`):

- `PYPI_API_TOKEN` — API token do PyPI (crie token em https://pypi.org/manage/account/token/).
- `DOCKERHUB_USERNAME` — nome de usuário do Docker Hub.
- `DOCKERHUB_TOKEN` — token de acesso do Docker Hub (ou password/API token).

Depois de adicionar os secrets, publique a Release (tag) no GitHub; o workflow `.github/workflows/publish.yml` irá rodar e enviar os artefatos ao PyPI e Docker Hub.
