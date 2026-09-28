# Demonstração — Verificação da REINF

> Projeto de portfólio de **Victória Pedrosa**. **Demonstração** de verificação automática da EFD-REINF — versão com dados fictícios (nomes, CNPJs, e-mails e IDs internos substituídos).

## Problema de negócio
Verificar se as empresas tinham movimento para a REINF exigia olhar os CSVs de prestado e tomado de cada uma.

## Antes x depois
| | Antes | Depois |
|---|---|---|
| Como é feito | Conferência manual pasta a pasta. | Script analisa os CSVs e gera a lista de empresas com e sem movimento. |

## Ganho
- Triagem da REINF em minutos.

## Tecnologias
Python, SQLite, pandas

## Arquivos
- `requirements.txt`
- `verificar_reinf.py`

## Como rodar
1. `pip install -r requirements.txt`
2. Copie `.env.exemplo` para `.env` e preencha os caminhos.
3. Execute o script principal.

## Autora
Victória Pedrosa — Product Owner do Time de IA, automação de processos contábeis e fiscais.
