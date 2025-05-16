from dotenv import load_dotenv
from agents import Categorizador, AnalistaFinanceiro
import sqlite3
from datetime import datetime
import uuid
import os

load_dotenv()

def inicializar_banco():
    """Garante que o banco de dados e tabelas existam"""
    try:
        os.makedirs('dados', exist_ok=True)
        with sqlite3.connect(os.getenv('DB_PATH', 'dados/transacoes.db')) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transacoes (
                    id TEXT PRIMARY KEY,
                    data TEXT,
                    valor REAL,
                    descricao TEXT,
                    categoria TEXT,
                    tags TEXT
                )
            ''')
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        exit(1)

def mostrar_relatorio(analista):
    periodo = input("Período (este_mes/mes_passado/este_ano/30_dias): ")
    try:
        dados = analista.obter_dados_periodo(periodo)
        sugestoes = analista.gerar_sugestoes(dados)
        
        print(f"\n📈 Relatório - {periodo}")
        print(f"🔹 Total de Ganhos: R$ {dados['total_ganhos']:.2f}")
        print(f"🔸 Total de Gastos: R$ {dados['total_gastos']:.2f}")
        
        print("\n📊 Distribuição por Categoria:")
        for cat, val in dados['dados'].items():
            print(f"- {cat}: R$ {val:.2f}")
        
        print("\n💡 Sugestões:")
        for sugestao in sugestoes:
            print(f"  {sugestao}")
            
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")

def mostrar_comparativo(analista):
    print("\n🔄 Comparativo de Períodos")
    print("Opções: este_mes, mes_passado, este_ano, 30_dias")
    periodo1 = input("Primeiro período: ")
    periodo2 = input("Segundo período: ")
    
    try:
        comparativo = analista.gerar_comparativo(periodo1, periodo2)
        
        print(f"\n📊 Comparativo entre {periodo1} e {periodo2}")
        print("\n🔍 Por Categoria:")
        for cat, dados in comparativo['comparativo'].items():
            print(f"- {cat}:")
            print(f"  {periodo1}: R$ {dados[periodo1]:.2f}")
            print(f"  {periodo2}: R$ {dados[periodo2]:.2f}")
            print(f"  Variação: R$ {dados['diferenca']:.2f} ({dados['variacao_percentual']:.1f}%)")
        
        print("\n📈 Resumo Geral:")
        print(f"Total de gastos:")
        print(f"  {periodo1}: R$ {comparativo['resumo']['total_gastos'][periodo1]:.2f}")
        print(f"  {periodo2}: R$ {comparativo['resumo']['total_gastos'][periodo2]:.2f}")
        print(f"  Diferença: R$ {comparativo['resumo']['total_gastos']['diferenca']:.2f}")
        
    except Exception as e:
        print(f"Erro ao gerar comparativo: {e}")

def main():
    categorizador = Categorizador()
    analista = AnalistaFinanceiro()
    inicializar_banco()

    while True:
        print("\n📊 Gerenciador Financeiro Pessoal")
        print("1. Adicionar Transação")
        print("2. Ver Relatório Completo")
        print("3. Comparativo entre Períodos")
        print("4. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            try:
                valor = float(input("Valor (negativo para gastos): "))
                descricao = input("Descrição: ")
                
                categoria = categorizador.categorizar(descricao)
                
                with sqlite3.connect(os.getenv('DB_PATH', 'dados/transacoes.db')) as conn:
                    conn.execute(
                        "INSERT INTO transacoes VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            str(uuid.uuid4()),
                            datetime.now().strftime('%Y-%m-%d'),
                            valor,
                            descricao,
                            categoria,
                            ""
                        )
                    )
                
                print(f"✅ Transação registrada como '{categoria}'")
                
            except ValueError:
                print("Erro: Digite um valor numérico válido!")
            except Exception as e:
                print(f"Erro ao registrar transação: {e}")
        
        elif opcao == "2":
            mostrar_relatorio(analista)
        
        elif opcao == "3":
            mostrar_comparativo(analista)
        
        elif opcao == "4":
            break

if __name__ == "__main__":
    main()