"""Tests de la extracción de texto por formato (los formatos de texto puro)."""
import json

import pytest

from src.ingestion.loaders import SUPPORTED_EXTENSIONS, extract_text


def test_formatos_soportados():
    for ext in [".pdf", ".docx", ".xlsx", ".pptx", ".md", ".csv", ".json", ".html"]:
        assert ext in SUPPORTED_EXTENSIONS


def test_extrae_json(tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"servicio": "TechRetail", "limite": 120}), encoding="utf-8")
    texto = extract_text(p)
    assert "servicio" in texto and "TechRetail" in texto
    assert "120" in texto


def test_extrae_csv_repite_encabezados(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("pasarela,comision\nMercadoPago,4.99\n", encoding="utf-8")
    texto = extract_text(p)
    assert "pasarela: MercadoPago" in texto
    assert "comision: 4.99" in texto


def test_extrae_markdown(tmp_path):
    p = tmp_path / "d.md"
    p.write_text("# Política\nContenido relevante.", encoding="utf-8")
    assert "Política" in extract_text(p)


def test_extrae_html_sin_ruido_tecnico(tmp_path):
    p = tmp_path / "d.html"
    p.write_text(
        "<html><body><h1>Bienvenido</h1><script>ruido()</script></body></html>",
        encoding="utf-8",
    )
    texto = extract_text(p)
    assert "Bienvenido" in texto
    assert "ruido" not in texto  # el contenido de <script> se elimina


def test_formato_no_soportado_lanza_error(tmp_path):
    p = tmp_path / "d.zip"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        extract_text(p)
