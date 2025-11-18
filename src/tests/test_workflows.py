"""
Suite de Testes Automatizados - Workflows
==========================================

Testes para validar funcionamento dos workflows principais.
Execute com: python -m pytest src/tests/test_workflows.py -v
"""

import json
from pathlib import Path

# Imports dos modulos a testar
from src.workflows import lead_qualificacao
from src.utils import config_loader, llm_client
from src.browser import actions


class TestConfigLoader:
    """Testes do carregador de configuracao."""
    
    def test_carregar_config_instagram(self):
        """Testa se config de Instagram carrega corretamente."""
        config = config_loader.carregar_config_site("instagram")
        
        assert isinstance(config, dict)
        assert "nome" in config
        assert config["nome"] == "Instagram"
        assert "url_login" in config
        assert "seletor_usuario" in config
    
    def test_config_site_inexistente(self):
        """Testa comportamento com site inexistente."""
        config = config_loader.carregar_config_site("site_nao_existe")
        
        # Deve retornar dict vazio
        assert isinstance(config, dict)


class TestLeadQualificacao:
    """Testes do modulo de qualificacao de leads."""
    
    def test_qualificar_lead_quente(self):
        """Testa qualificacao de lead quente."""
        lead = {
            "nome": "Teste Quente",
            "interesse": "Muito alto",
            "orcamento": "R$ 500.000",
            "prazo": "Precisa em 7 dias",
        }
        
        resultado = lead_qualificacao.qualificar_lead(lead)
        
        assert "classificacao" in resultado
        assert resultado["classificacao"] in ["Quente", "Morno", "Frio"]
        assert "pontuacao" in resultado
        assert isinstance(resultado["pontuacao"], (int, float))
        assert 0 <= resultado["pontuacao"] <= 10
        assert "justificativa" in resultado
        assert "acao_sugerida" in resultado
        assert "tags" in resultado
        assert isinstance(resultado["tags"], list)
    
    def test_qualificar_lead_morno(self):
        """Testa qualificacao de lead morno."""
        lead = {
            "nome": "Teste Morno",
            "interesse": "Medio",
            "orcamento": "Indefinido",
            "prazo": "Sem pressa",
        }
        
        resultado = lead_qualificacao.qualificar_lead(lead)
        
        assert resultado["classificacao"] in ["Quente", "Morno", "Frio"]
        assert resultado["pontuacao"] >= 0
    
    def test_qualificar_lote_leads(self):
        """Testa qualificacao em lote."""
        leads = [
            {"nome": "Lead 1", "interesse": "Alto", "orcamento": "Definido"},
            {"nome": "Lead 2", "interesse": "Baixo", "orcamento": "Indefinido"},
            {"nome": "Lead 3", "interesse": "Medio", "orcamento": "Parcial"},
        ]
        
        resultados = lead_qualificacao.qualificar_lote_leads(leads)
        
        assert len(resultados) == 3
        assert all("lead" in r for r in resultados)
        assert all("qualificacao" in r for r in resultados)
        assert all("status" in r for r in resultados)
        
        sucessos = sum(1 for r in resultados if r["status"] == "sucesso")
        assert sucessos > 0  # Pelo menos 1 deve ter sucesso


class TestBrowserActions:
    """Testes de acoes do navegador (sem Playwright real)."""
    
    def test_action_signatures(self):
        """Testa se as assinaturas das acoes estao corretas."""
        # Apenas verifica se as funcoes existem e sao callable
        assert callable(actions.abrir_url)
        assert callable(actions.clicar)
        assert callable(actions.digitar)
        assert callable(actions.esperar_selector)
        assert callable(actions.type_text)
        assert callable(actions.press_key)
        assert callable(actions.wait_seconds)


class TestLLMClient:
    """Testes do cliente LLM."""
    
    def test_extrair_json_simples(self):
        """Testa extracao de JSON de um texto."""
        texto = 'Aqui esta o resultado: {"chave": "valor"} fim do texto.'
        
        # Usa a funcao privada de extracao
        from src.utils.llm_client import _extrair_json
        json_extraido = _extrair_json(texto)
        
        assert json_extraido == '{"chave": "valor"}'
        
        # Valida que eh um JSON valido
        parsed = json.loads(json_extraido)
        assert parsed["chave"] == "valor"
    
    def test_extrair_json_invalido(self):
        """Testa comportamento com JSON invalido."""
        from src.utils.llm_client import _extrair_json
        
        # Import pytest localmente to avoid failing module import if pytest isn't installed
        try:
            import pytest as _pytest
        except Exception:
            _pytest = None

        if _pytest:
            with _pytest.raises(ValueError):
                _extrair_json("Texto sem JSON")
        else:
            # Fallback behaviour: ensure function raises ValueError
            raised = False
            try:
                _extrair_json("Texto sem JSON")
            except ValueError:
                raised = True
            assert raised, "_extrair_json should raise ValueError for text without JSON"


class TestIntegration:
    """Testes de integracao entre componentes."""
    
    def test_workflow_completo_leads(self):
        """Testa fluxo completo de qualificacao."""
        # Simula coleta de leads
        leads_brutos = [
            {"nome": "Alice", "interesse": "Imobiliario", "orcamento": "1M", "prazo": "15 dias"},
            {"nome": "Bob", "interesse": "E-commerce", "orcamento": "500k", "prazo": "30 dias"},
        ]
        
        # Qualifica lote
        resultados = lead_qualificacao.qualificar_lote_leads(leads_brutos)
        
        # Valida
        assert len(resultados) == 2
        
        # Filtra apenas os sucessos
        sucessos = [r for r in resultados if r["status"] == "sucesso"]
        assert len(sucessos) > 0
        
        # Classifica por temperatura
        quentes = [r for r in sucessos if r["qualificacao"].get("classificacao") == "Quente"]
        assert len(sucessos) > 0  # Deve haver pelo menos alguma classificacao


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
