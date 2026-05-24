"""Testes do carregador de config do escritorio (load_firm_config)."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from whatsapp import load_firm_config

def _write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def test_arquivo_ausente_retorna_defaults():
    cfg = load_firm_config("/caminho/que/nao/existe.json")
    assert cfg["team_names"] == [], "sem arquivo, equipe deve ser vazia"
    assert cfg["thresholds"]["atrasada_hours"] == 24
    assert cfg["thresholds"]["importante_hours"] == 4
    assert cfg["thresholds"]["normal_hours"] == 1
    assert "audiencia" in cfg["urgent_keywords"], "keywords juridicas sao default"
    assert "jusbrasil" in cfg["silence_keywords"], "saas comuns sao default"
    assert cfg["max_chats"] == 100 and cfg["max_process"] == 30
    print("OK test_arquivo_ausente_retorna_defaults")

def test_equipe_do_arquivo_vira_lista_plana_minuscula():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "config.json")
        _write(p, {"team": [
            {"display": "Dra. Ana", "area": "Civel", "names": ["Ana", "DRA ANA"]},
            {"display": "Dr. Bruno", "area": "Trabalhista", "names": ["Bruno"]},
        ]})
        cfg = load_firm_config(p)
        assert cfg["team_names"] == ["ana", "dra ana", "bruno"], cfg["team_names"]
    print("OK test_equipe_do_arquivo_vira_lista_plana_minuscula")

def test_arquivo_sobrescreve_thresholds_e_keywords():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "config.json")
        _write(p, {
            "triagem": {"thresholds": {"atrasada_hours": 48, "importante_hours": 8, "normal_hours": 2},
                        "max_chats": 200, "max_process": 50},
            "urgent_keywords": ["marca", "inpi"],
            "silence_keywords": ["spam"],
        })
        cfg = load_firm_config(p)
        assert cfg["thresholds"]["atrasada_hours"] == 48
        assert cfg["thresholds"]["importante_hours"] == 8
        assert cfg["thresholds"]["normal_hours"] == 2
        assert cfg["max_chats"] == 200 and cfg["max_process"] == 50
        assert cfg["urgent_keywords"] == ["marca", "inpi"]
        assert cfg["silence_keywords"] == ["spam"]
    print("OK test_arquivo_sobrescreve_thresholds_e_keywords")

def test_json_invalido_cai_em_defaults_sem_quebrar():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "config.json")
        with open(p, "w", encoding="utf-8") as f:
            f.write("{ isto nao e json }")
        cfg = load_firm_config(p)
        assert cfg["thresholds"]["atrasada_hours"] == 24, "JSON quebrado deve cair em defaults"
    print("OK test_json_invalido_cai_em_defaults_sem_quebrar")

if __name__ == "__main__":
    test_arquivo_ausente_retorna_defaults()
    test_equipe_do_arquivo_vira_lista_plana_minuscula()
    test_arquivo_sobrescreve_thresholds_e_keywords()
    test_json_invalido_cai_em_defaults_sem_quebrar()
    print("\nTODOS OS TESTES PASSARAM")
