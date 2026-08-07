"""Tests de la limpieza de texto y el chunking."""
from src.ingestion.chunking import dividir_en_chunks, limpiar_texto


def test_limpiar_colapsa_espacios():
    assert limpiar_texto("hola    mundo") == "hola mundo"


def test_limpiar_colapsa_saltos_de_linea():
    assert "\n\n\n" not in limpiar_texto("a\n\n\n\n\nb")


def test_dividir_texto_vacio_devuelve_lista_vacia():
    assert dividir_en_chunks("") == []
    assert dividir_en_chunks("   \n  ") == []


def test_dividir_devuelve_chunks_no_vacios():
    texto = "Este es un párrafo de ejemplo.\n\n" * 200
    chunks = dividir_en_chunks(texto, chunk_size=100, overlap=20)
    assert len(chunks) >= 1
    assert all(isinstance(c, str) and c.strip() for c in chunks)


def test_parrafo_gigante_se_parte():
    # Un único párrafo mucho mayor al chunk_size debe partirse en varios trozos.
    parrafo = "palabra " * 500
    chunks = dividir_en_chunks(parrafo, chunk_size=50, overlap=10)
    assert len(chunks) > 1
