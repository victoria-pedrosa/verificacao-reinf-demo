import os
import pandas as pd
import re
from dotenv import load_dotenv
load_dotenv()  # lê o .env local (não vai para o GitHub)

# ================= CONFIGURAÇÕES =================
# Coloque aqui a pasta raiz onde o robô guarda as informações
DIRETORIO_RAIZ = os.getenv("DIRETORIO_RAIZ")

PLANILHA_MESTRE = "empresas.xlsx"
ABA_MESTRE = "TABELÃO 2002" 
ARQUIVO_SAIDA = "empresas_atualizado_REINF.xlsx"

COLUNAS_TOMADO = ['PIS', 'COFINS', 'INSS', 'IRPJ', 'CSLL']
# =================================================

def limpa_valor_monetario(serie):
    """Converte formato monetário (ex: 1.500,00) para número e verifica se é > 0."""
    serie_limpa = serie.astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    valores_numericos = pd.to_numeric(serie_limpa, errors='coerce').fillna(0)
    return (valores_numericos > 0).any()

retencao_por_empresa = {}
ficheiros_encontrados = 0

print(f"🔍 Varrendo a pasta: {DIRETORIO_RAIZ}")

for root, dirs, files in os.walk(DIRETORIO_RAIZ):
    for arquivo in files:
        nome_arquivo_lower = arquivo.lower()
        
        # Só analisa os CSVs de prestado e tomado
        if nome_arquivo_lower in ['nfse_csv_prestado.csv', 'nfse_csv_tomado.csv']:
            ficheiros_encontrados += 1
            caminho_completo = os.path.join(root, arquivo)
            
            # Divide o caminho em partes
            partes_caminho = root.replace('\\', '/').split('/')
            codigo_emp = None
            
            # Analisa as pastas de trás para a frente para achar a pasta "CODIGO-NOME"
            for parte in reversed(partes_caminho):
                # Procura EXATAMENTE por números seguidos de um traço/hífen (Ex: "8-SANTE")
                match = re.match(r'^(\d+)\s*[-_]', parte)
                if match:
                    codigo_emp = int(match.group(1))
                    break # Achou o código, para de subir nas pastas
            
            # Se não achou o código com traço, ignora este ficheiro e avisa
            if codigo_emp is None:
                print(f"⚠️ Ficheiro ignorado (não achou pasta CODIGO-NOME): {caminho_completo}")
                continue
            
            # Regista a empresa no dicionário (se ainda não existir)
            if codigo_emp not in retencao_por_empresa:
                retencao_por_empresa[codigo_emp] = False
            
            # Se já analisou outro arquivo da mesma empresa e achou retenção, pula
            if retencao_por_empresa[codigo_emp]:
                continue

            # Lê o CSV para verificar retenção
            try:
                df = pd.read_csv(caminho_completo, sep=';', encoding='latin1')
                
                if nome_arquivo_lower == 'nfse_csv_prestado.csv':
                    if 'INSS' in df.columns and limpa_valor_monetario(df['INSS']):
                        retencao_por_empresa[codigo_emp] = True
                        print(f"✅ Retenção encontrada (INSS Prestado) - Empresa {codigo_emp}")
                
                elif nome_arquivo_lower == 'nfse_csv_tomado.csv':
                    for col in COLUNAS_TOMADO:
                        if col in df.columns and limpa_valor_monetario(df[col]):
                            retencao_por_empresa[codigo_emp] = True
                            print(f"✅ Retenção encontrada ({col} Tomado) - Empresa {codigo_emp}")
                            break
            except Exception as e:
                print(f"❌ Erro ao ler CSV {caminho_completo}: {e}")

print(f"\nTotal de ficheiros CSV lidos: {ficheiros_encontrados}")

if ficheiros_encontrados > 0:
    resultados_reinf = {cod: ("COM RETENÇÃO" if tem else "SEM RETENÇÃO") for cod, tem in retencao_por_empresa.items()}

    print("\n📊 Atualizando a planilha mestre...")
    try:
        df_mestre = pd.read_excel(PLANILHA_MESTRE, sheet_name=ABA_MESTRE)
        df_mestre['Código Dominio'] = pd.to_numeric(df_mestre['Código Dominio'], errors='coerce')
        
        # Mapeia e preenche a nova coluna
        df_mestre['STATUS REINF CALCULADO'] = df_mestre['Código Dominio'].map(resultados_reinf)
        df_mestre['STATUS REINF CALCULADO'] = df_mestre['STATUS REINF CALCULADO'].fillna("NÃO AVALIADO (SEM CSV)")

        df_mestre.to_excel(ARQUIVO_SAIDA, index=False)
        print(f"✅ Sucesso! Planilha gerada: {ARQUIVO_SAIDA}")

    except Exception as e:
        print(f"❌ Erro ao processar o Excel mestre: {e}")
else:
    print("\n⚠️ Nenhum CSV foi encontrado. Verifique se o DIRETORIO_RAIZ está correto.")