from datetime import datetime, timedelta
import sqlite3
import os
from typing import Dict, List, Tuple

class AnalistaFinanceiro:
    def __init__(self):
        self.db_path = os.getenv('DB_PATH', 'dados/transacoes.db')
        
    def _calcular_intervalo(self, periodo: str) -> Tuple[str, str]:
        hoje = datetime.now().date()
        if periodo == "este_mes":
            return (hoje.replace(day=1).strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d'))
        elif periodo == "mes_passado":
            ultimo_dia = hoje.replace(day=1) - timedelta(days=1)
            return (ultimo_dia.replace(day=1).strftime('%Y-%m-%d'), ultimo_dia.strftime('%Y-%m-%d'))
        elif periodo == "este_ano":
            return (hoje.replace(month=1, day=1).strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d'))
        else: 
            return ((hoje - timedelta(days=30)).strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d'))

    def obter_dados_periodo(self, periodo: str) -> Dict:
        inicio, fim = self._calcular_intervalo(periodo)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT categoria, SUM(valor) as total
                FROM transacoes
                WHERE data BETWEEN ? AND ?
                GROUP BY categoria
            """, (inicio, fim))
            
            dados = cursor.fetchall()

        return {
            'periodo': periodo,
            'dados': {row['categoria']: row['total'] for row in dados},
            'total_gastos': sum(abs(row['total']) for row in dados if row['total'] < 0),
            'total_ganhos': sum(row['total'] for row in dados if row['total'] > 0)
        }

    def gerar_comparativo(self, periodo1: str, periodo2: str) -> Dict:
        dados1 = self.obter_dados_periodo(periodo1)
        dados2 = self.obter_dados_periodo(periodo2)
        
        categorias = set(dados1['dados'].keys()).union(set(dados2['dados'].keys()))
        comparativo = {}
        
        for cat in categorias:
            valor1 = dados1['dados'].get(cat, 0)
            valor2 = dados2['dados'].get(cat, 0)
            diferenca = valor2 - valor1
            variacao = (diferenca / abs(valor1)) * 100 if valor1 != 0 else float('inf')
            
            comparativo[cat] = {
                periodo1: valor1,
                periodo2: valor2,
                'diferenca': diferenca,
                'variacao_percentual': variacao
            }
        
        return {
            'periodos': [periodo1, periodo2],
            'comparativo': comparativo,
            'resumo': {
                'total_gastos': {
                    periodo1: dados1['total_gastos'],
                    periodo2: dados2['total_gastos'],
                    'diferenca': dados2['total_gastos'] - dados1['total_gastos']
                },
                'total_ganhos': {
                    periodo1: dados1['total_ganhos'],
                    periodo2: dados2['total_ganhos'],
                    'diferenca': dados2['total_ganhos'] - dados1['total_ganhos']
                }
            }
        }

    def gerar_sugestoes(self, dados: Dict) -> List[str]:
        sugestoes = []
        categorias = dados['dados']
        
        # Sugestão 1: Categorias com maior gasto
        top_gastos = sorted(
            [(cat, abs(val)) for cat, val in categorias.items() if val < 0],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if top_gastos:
            sugestoes.append(
                f"🔴 Maiores gastos: {', '.join([f'{cat} (R${val:.2f})' for cat, val in top_gastos])}"
            )
        
        # Sugestão 2: Comparativo com mês anterior
        if 'mes_passado' in dados['periodo']:
            comparativo = self.gerar_comparativo('mes_passado', 'este_mes')
            for cat, dados_cat in comparativo['comparativo'].items():
                if dados_cat['variacao_percentual'] > 20 and dados_cat[comparativo['periodos'][1]] < 0:
                    sugestoes.append(
                        f"⚠️ Aumento de {abs(dados_cat['variacao_percentual']):.1f}% em {cat}"
                    )
        
        # Sugestão 3: Economia potencial
        gastos_recorrentes = ['Moradia', 'Transporte', 'Assinaturas']
        for cat in gastos_recorrentes:
            if cat in categorias and categorias[cat] < 0:
                sugestoes.append(
                    f"💡 Reveja gastos com {cat} - potencial economia de até {(abs(categorias[cat]) * 0.15):.2f}"
                )
        
        return sugestoes if sugestoes else ["✅ Seus gastos estão equilibrados este mês"]