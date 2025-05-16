import ollama
import os
from typing import List

class Categorizador:
    CATEGORIAS: List[str] = [
        "Alimentação", "Transporte", "Moradia", 
        "Saúde", "Educação", "Lazer", "Trabalho",
        "Serviços", "Impostos", "Vestimentas", "Investimentos", "Outros"
    ]

    def __init__(self):
        self.modelo = os.getenv('MODELO_FINANCEIRO', 'qwen:7b')
        self.verificar_modelo()

    def verificar_modelo(self):
        """Verifica se o modelo está disponível localmente"""
        try:
            ollama.show(self.modelo)
        except Exception:
            print(f"⚠️ Modelo '{self.modelo}' não encontrado. Usando 'llama3' como fallback.")
            self.modelo = 'llama3'

    def categorizar(self, descricao: str) -> str:
        """Categoriza transações usando IA com fallback seguro"""
        try:
            resposta = ollama.chat(
                model=self.modelo,
                messages=[{
                    'role': 'user',
                    'content': (
                        f"Classifique a transação '{descricao}' em uma destas categorias: "
                        f"{', '.join(self.CATEGORIAS)}. "
                        "Responda APENAS com o nome exato da categoria em português."
                    )
                }]
            )
            categoria = resposta['message']['content'].strip()
            return categoria if categoria in self.CATEGORIAS else "Outros"
        except Exception as e:
            print(f"⚠️ Falha na categorização: {str(e)}. Usando 'Outros'.")
            return "Outros"