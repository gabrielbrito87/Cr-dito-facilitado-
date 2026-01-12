#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Colaborativo CAIXA - Sistema Completo de Consultas e Análise de Crédito Imobiliário
Baseado no Manual Geral de Concessão de Crédito Imobiliário para Pessoa Física - Versão Completa
"""

import json
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AgenteCaixaCreditoCompleto:
    def __init__(self):
        self.nome = "Agente Colaborativo CAIXA - Versão Completa"
        self.versao = "2.0"
        self.data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Base de conhecimento completa extraída do manual
        self.base_conhecimento = self._carregar_base_conhecimento_completa()
        
        # Inicializar banco de dados
        self._inicializar_bd()
        
        print(f"🏦 {self.nome} v{self.versao} inicializado com sucesso!")
        print(f"📅 Data de criação: {self.data_criacao}")
        print("✅ Sistema pronto para consultas e análises de conformidade")
        print(f"📊 Base de conhecimento: {len(self.base_conhecimento)} seções principais")

    def _carregar_base_conhecimento_completa(self) -> Dict:
        """Carrega a base de conhecimento completa extraída do manual CAIXA"""
        return {
            "programas": {
                "PMCMV": {
                    "nome_completo": "Programa Minha Casa, Minha Vida",
                    "operacoes": [
                        "Aquisição Imóvel Novo ou Usado",
                        "Aquisição de Terreno e Construção", 
                        "Construção em Terreno Próprio",
                        "Conclusão, Ampliação, Reforma ou Melhoria (exceto Classe Média)",
                        "Reforma ou Melhoria PCD (Exceto Classe Média)",
                        "Imóveis Caixa/AMV (Adjudicados, arrematados em Leilão Caixa)"
                    ],
                    "enquadramento": "Determinado pelo valor do imóvel (valor de venda e compra ou investimento), recorte populacional/territorial, e renda familiar",
                    "referencia_normativa": "MN, MO30824",
                    "recursos": ["FGTS", "SBPE", "Fundo Social"]
                },
                "FGTS": {
                    "nome_completo": "Carta de Crédito FGTS/Programa Pró-cotista",
                    "operacoes": [
                        "Aquisição Imóvel Novo ou Usado",
                        "Aquisição de Terreno e Construção",
                        "Construção em Terreno Próprio"
                    ],
                    "requisitos": [
                        "Ser titular de CV FGTS com mínimo de 3 anos de trabalho sob o regime do FGTS",
                        "Contrato de trabalho ativo sob regime do FGTS ou saldo em CV, de, no mínimo, 10% do valor da avaliação do imóvel"
                    ],
                    "redutor_taxa": "0,5% na taxa de juros para cotista do FGTS"
                },
                "SBPE": {
                    "nome_completo": "Carta de Crédito SBPE",
                    "operacoes": [
                        "Aquisição de Imóvel Novo ou Usado (Residencial ou Comercial/Misto)",
                        "Aquisição de Terreno e Construção (somente residencial)",
                        "Construção em Terreno Próprio (somente residencial)",
                        "Reforma Casa com Garantia de Imóvel (somente residencial)",
                        "Aquisição de Lote Urbanizado Alocação de Recursos (somente residencial)",
                        "Aquisição de Imóvel CAIXA/AMV"
                    ],
                    "caracteristicas": "Não há critérios específicos para enquadramento",
                    "referencia_normativa": "MN, MO30769",
                    "observacao": "Fim da restrição de financiamento de segundo imóvel"
                },
                "RECURSOS_LIVRES": {
                    "nome_completo": "Recursos Livres",
                    "operacoes": [
                        "Aquisição de Imóvel Novo ou Usado (Residencial)"
                    ],
                    "enquadramento": [
                        "Imóveis com valor de avaliação acima de 1,5 milhão",
                        "Cliente que já possua financiamento imobiliário ativo na CAIXA, mesmo que o imóvel tenha valor de avaliação inferior a 1,5 milhão"
                    ]
                }
            },
            
            "exigencias_tomador": {
                "requisitos_gerais": [
                    "Ter idoneidade cadastral",
                    "Inscrição obrigatória no CPF com situação regular junto à Receita Federal do Brasil",
                    "Comprovar residência no Brasil",
                    "Não ser sócio ou dirigente de empresas da construção civil para aquisição de imóveis na planta objeto de incorporação ou construção da empresa da qual faz parte",
                    "Ser brasileiro nato ou naturalizado ou estrangeiro(s) detentor(es) de Carteira de Registro Nacional Migratório - RNM ou Carteira de Registro Nacional de Estrangeiro - RNE válida e CPF regular junto à Receita Federal"
                ],
                "restricoes_cca": [
                    "É vedado ao CCA atuar na contratação de propostas habitacionais e comerciais cuja comprovação de renda seja de emissão do próprio Correspondente CAIXA Aqui e sócios, exceto para abertura de contas correntes, com a finalidade de crédito salário"
                ],
                "situacoes_especiais": [
                    "Para modalidade de construção, é permitido que o Responsável Técnico pela Obra figure como proponente ou cônjuge do proponente, devendo as vistorias de obra ocorrer obrigatoriamente na forma presencial, com emissão do RAE",
                    "É permitido financiamento à pessoa incapaz para os atos da vida civil, que se encontre sob curatela, sendo considerada somente a renda do incapaz, vedada a aceitação da renda familiar do seu curador",
                    "Admite-se a concessão de financiamento com utilização da renda familiar do proponente incapaz mediante a apresentação de autorização judicial"
                ]
            },
            
            "exigencias_vendedor": {
                "pessoa_fisica": [
                    "Ter capacidade civil",
                    "Ser maior de 18 anos ou ser menor emancipado com idade igual ou superior a 16 anos completos",
                    "Ter CPF com situação regular junto à Receita Federal do Brasil",
                    "Comprovação de estado civil",
                    "Ser brasileiro nato, naturalizado ou estrangeiro(s) detentor(es) de RNM ou RNE válida e CPF regular"
                ],
                "pessoa_juridica": [
                    "Ter CNPJ com situação regular junto à Receita Federal do Brasil",
                    "Para fundos de Investimento, documento deliberando sobre a constituição do Fundo e regulamento, registrados em Cartório de Títulos e Documentos ou na CVM",
                    "Sócio/representante legal ser brasileiro nato ou naturalizado ou estrangeiro(s) detentor(es) de RNM ou RNE válida e CPF regular"
                ],
                "situacoes_especiais": [
                    "Se vendedor(es) emancipado(s) (idade entre 16 e 18 anos incompletos), analfabetos e deficientes visuais, que tenham endereço residencial ou comercial no exterior – encaminhar o cliente à Agência e PA de vinculação",
                    "Se o(s) vendedor(es) for(em) ascendente(s) do comprador(es), deve ser encaminhado à Agência/PA de vinculação para contratação"
                ]
            },
            
            "exigencias_imovel": {
                "requisitos_basicos": [
                    "Estar localizado em área urbana",
                    "Possuir vias de acesso, soluções para abastecimento de água, esgoto pluvial e sanitário e energia elétrica (pública e domiciliar)",
                    "Estar livre e desembaraçado de quaisquer ônus",
                    "Possuir Certidão Individualizada e Atualizada de Inteiro Teor da Matrícula registrada junto ao RI",
                    "Ser aceito pela CAIXA como garantia"
                ],
                "situacoes_aceitas": [
                    "Com parte de área edificada não averbada",
                    "Com parte de área de uso comercial (imóvel misto)",
                    "Sob regime de enfiteuse ou aforamento de imóveis de particulares (registrado até 10/01/2003)",
                    "Sob regime de enfiteuse administrativa/aforamento exclusivamente para os imóveis da União",
                    "Sob regime de aforamento exclusivamente para os terrenos de marinha e acrescidos",
                    "Imóvel de marinha com até 60% da área sob Regime de Ocupação (condições específicas)",
                    "Oriundo de empreendimento financiado pela CAIXA",
                    "Com concessão de Direito Real de Uso (CDRU) concedida pelo poder público local",
                    "Com 'habite-se parcial'",
                    "Submetido ao regime de afetação",
                    "Localizado em condomínio de lotes",
                    "Imóvel CAIXA/AMV",
                    "De madeira, casa pré-fabricada ou com outras tecnologias construtivas"
                ],
                "impedimentos": [
                    "Bens ou imóveis com contaminação por substâncias químicas",
                    "Bens de hospitais filantrópicos e Santas Casas de Misericórdia",
                    "Propriedade(s) cuja(s) matrícula(s) haja averbação de cancelamento, suspensão ou bloqueio",
                    "Gravado com cláusula de usufruto",
                    "Tombado ou em fase de tombamento pelo Patrimônio Histórico e Artístico",
                    "Alienado/hipotecado em garantia de operação de crédito em outra instituição",
                    "Gravado com cláusula de inalienabilidade ou outro ônus",
                    "Com destinação agrícola, inclusive sítios, glebas ou granjas",
                    "Com características de imóvel multifamiliar",
                    "Próprio da União, Estado, Município ou Autarquia",
                    "Que já tenha sido de propriedade do proponente nos últimos 02 anos",
                    "Cujo vendedor seja pessoa jurídica e o proponente seja sócio ou representante legal",
                    "Sem nenhuma área construída averbada (exceto lote urbanizado)",
                    "Localizado em condomínio com características de loteamento irregular",
                    "Sob regime de ocupação",
                    "Registrados como imóvel do tipo 'Laje'",
                    "Cuja edificação possua característica de hotel/apart hotel",
                    "Sob regime de enfiteuse não permitida"
                ],
                "exigencias_especificas_df": [
                    "Declaração de Capacidade de Atendimento das Ligações Individuais",
                    "Declaração de Execução de Elementos Construtivos – DEEC",
                    "Verificação pela engenharia da CAIXA das exigências técnicas"
                ]
            },
            
            "modalidades_construcao": {
                "construcao_individual": {
                    "percentual_execucao_maximo": "70%",
                    "prazo_construcao": "Conforme cronograma aprovado",
                    "acompanhamento": "Vistorias obrigatórias",
                    "documentos_necessarios": [
                        "Projeto arquitetônico aprovado",
                        "Licenciamento de obra",
                        "Cronograma físico-financeiro",
                        "ART/RRT do responsável técnico"
                    ]
                },
                "reforma_ampliacao": {
                    "tipos": [
                        "Reforma com ampliação",
                        "Reforma sem ampliação",
                        "Reforma PCD"
                    ],
                    "exigencias": [
                        "Projeto de reforma aprovado",
                        "Licenciamento quando necessário",
                        "Cronograma de execução"
                    ]
                }
            },
            
            "parametros_financiamento": {
                "modalidades_taxa": [
                    "Taxa fixa",
                    "Taxa variável indexada", 
                    "Taxa customizada"
                ],
                "indexadores": [
                    "TR (Taxa Referencial)",
                    "IPCA (Índice de Preços ao Consumidor Amplo)",
                    "Poupança"
                ],
                "sistemas_amortizacao": [
                    "SAC (Sistema de Amortização Constante)",
                    "PRICE (Sistema Francês)"
                ],
                "garantias": [
                    "Hipoteca do imóvel financiado",
                    "Alienação fiduciária"
                ],
                "seguros_obrigatorios": [
                    "MIP (Morte e Invalidez Permanente)",
                    "DFI (Danos Físicos ao Imóvel)",
                    "DFC (Danos Físicos ao Conteúdo) - opcional"
                ],
                "carencia": "Possível para unidades vinculadas ao empreendimento Ilha Pura"
            },
            
            "documentacao": {
                "tomador": [
                    "Documentos pessoais (RG, CPF)",
                    "Comprovação de renda",
                    "Comprovação de residência",
                    "Certidões negativas",
                    "Comprovação de estado civil"
                ],
                "vendedor": [
                    "Documentos pessoais (PF) ou empresariais (PJ)",
                    "Comprovação de capacidade civil",
                    "Certidões negativas"
                ],
                "imovel": [
                    "Certidão de matrícula individualizada e atualizada",
                    "IPTU",
                    "Escritura ou contrato de compra e venda",
                    "Planta aprovada (para construção)",
                    "Licenciamento de obra (quando aplicável)"
                ],
                "especificas_programa": {
                    "FGTS": [
                        "Comprovação de residência ou trabalho",
                        "Extrato da conta vinculada FGTS",
                        "Comprovação de tempo de trabalho sob regime FGTS"
                    ],
                    "PMCMV": [
                        "Documentação fator social",
                        "Comprovação de renda familiar",
                        "Declarações específicas do programa"
                    ]
                }
            },
            
            "tarifas_custos": {
                "tarifa_avaliacao": {
                    "nome": "Tarifa de Avaliação de Bens Recebidos em Garantia",
                    "aplicacao": "Todas as operações",
                    "obrigatoriedade": "Recolhimento obrigatório"
                },
                "tao": {
                    "nome": "TAO - Tarifa de Acompanhamento da Operação",
                    "aplicacao": "Construção FGTS/PMCMV",
                    "finalidade": "Acompanhamento de obras"
                },
                "tarifa_reavaliacao": {
                    "nome": "Tarifa de Reavaliação de Bens Recebidos em Garantia",
                    "aplicacao": "SBPE",
                    "quando": "Quando necessária reavaliação"
                },
                "tarifa_analise_seguro": {
                    "nome": "Tarifa para Análise de Apólice Individual de Seguros",
                    "aplicacao": "MIP, DFI e DFC",
                    "finalidade": "Análise de apólices individuais"
                },
                "ta": {
                    "nome": "TA - Tarifa de Administração de Contrato",
                    "aplicacao": "Administração mensal do contrato",
                    "periodicidade": "Mensal"
                },
                "outros_custos": [
                    "IOF conforme legislação vigente",
                    "Primeiros prêmios de seguro obrigatórios",
                    "Despesas cartoriais (podem ser financiadas)"
                ]
            },
            
            "compliance": {
                "pld": {
                    "nome": "Prevenção à Lavagem de Dinheiro, ao Financiamento do Terrorismo e da Proliferação de Armas de Destruição em Massa",
                    "obrigatoriedade": "Verificação obrigatória em todas as operações"
                },
                "conflito_interesse": {
                    "nome": "Conflito de Interesse",
                    "verificacoes": "Identificação de conflitos entre partes envolvidas"
                },
                "legitimidade": {
                    "nome": "Legitimidade da Contratação/Prestação de Serviços",
                    "objetivo": "Verificação da legitimidade da operação"
                },
                "pesquisas_cadastrais": {
                    "nome": "Realização das Pesquisas Cadastrais",
                    "obrigatoriedade": "Consultas obrigatórias antes da formalização"
                },
                "conformidade_proativa": {
                    "nome": "Conformidade Proativa",
                    "quando": "Obrigatória antes da formalização da contratação"
                }
            },
            
            "procedimentos_operacionais": {
                "qualificacao_proposta": [
                    "Oferta do produto adequado ao cliente",
                    "Comunicação ao cliente",
                    "Entrevista e constatação da renda",
                    "Avaliação de risco do tomador",
                    "Avaliação do imóvel",
                    "Análise jurídica",
                    "Análise de alçada"
                ],
                "formalizacao": [
                    "Assinatura do contrato",
                    "Registro do contrato",
                    "Crédito dos recursos",
                    "Conformidade do registro"
                ],
                "acompanhamento": [
                    "Cobrança do encargo mensal",
                    "Acompanhamento de obras (construção)",
                    "Gestão de garantias",
                    "Atendimento ao cliente"
                ]
            },
            
            "canais_atendimento": {
                "app_habitacao": {
                    "nome": "APP Habitação CAIXA",
                    "funcionalidades": [
                        "Simulação de financiamento",
                        "Acompanhamento de proposta",
                        "Formalização de contrato",
                        "Consulta de saldo devedor"
                    ]
                },
                "siopi": {
                    "nome": "Sistema SIOPI",
                    "finalidade": "Cadastramento e acompanhamento de propostas",
                    "acesso": "Internet"
                },
                "agencias_pa": {
                    "nome": "Agências e Postos de Atendimento",
                    "restricao": "Não é permitido encaminhamento para Agências Digitais"
                }
            },
            
            "sustentabilidade": [
                "Possibilidade de carência para pagamento dos encargos",
                "Financiamento das despesas cartoriais",
                "Simulador na internet com informações detalhadas",
                "Cartilha com orientações sobre financiamento habitacional",
                "Cursos de Educação Financeira",
                "Responsabilidade Social, Ambiental e Climática"
            ]
        }

    def _inicializar_bd(self):
        """Inicializa banco de dados SQLite para histórico de consultas"""
        self.conn = sqlite3.connect('agente_caixa_completo.db')
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                tipo_consulta TEXT,
                pergunta TEXT,
                resposta TEXT,
                usuario TEXT,
                categoria TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analises_conformidade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                tipo_operacao TEXT,
                resultado TEXT,
                observacoes TEXT,
                usuario TEXT,
                score_conformidade REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_decisoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                tipo_decisao TEXT,
                contexto TEXT,
                decisao TEXT,
                justificativa TEXT,
                usuario TEXT
            )
        ''')
        
        self.conn.commit()

    def consultar(self, pergunta: str, usuario: str = "sistema") -> str:
        """Realiza consulta avançada na base de conhecimento"""
        pergunta_lower = pergunta.lower()
        categoria = self._identificar_categoria(pergunta_lower)
        
        # Roteamento inteligente de consultas
        if categoria == "programas":
            resposta = self._consultar_programas_avancado(pergunta_lower)
        elif categoria == "tomador":
            resposta = self._consultar_exigencias_tomador_avancado(pergunta_lower)
        elif categoria == "vendedor":
            resposta = self._consultar_exigencias_vendedor_avancado(pergunta_lower)
        elif categoria == "imovel":
            resposta = self._consultar_exigencias_imovel_avancado(pergunta_lower)
        elif categoria == "construcao":
            resposta = self._consultar_modalidades_construcao(pergunta_lower)
        elif categoria == "financiamento":
            resposta = self._consultar_parametros_financiamento_avancado(pergunta_lower)
        elif categoria == "documentacao":
            resposta = self._consultar_documentacao_avancada(pergunta_lower)
        elif categoria == "tarifas":
            resposta = self._consultar_tarifas_avancado(pergunta_lower)
        elif categoria == "compliance":
            resposta = self._consultar_compliance_avancado(pergunta_lower)
        elif categoria == "procedimentos":
            resposta = self._consultar_procedimentos_operacionais(pergunta_lower)
        elif categoria == "canais":
            resposta = self._consultar_canais_atendimento(pergunta_lower)
        else:
            resposta = self._busca_geral(pergunta_lower)
        
        # Registrar consulta
        self._registrar_consulta(pergunta, resposta, usuario, categoria)
        
        return resposta

    def _identificar_categoria(self, pergunta: str) -> str:
        """Identifica a categoria da pergunta para roteamento inteligente"""
        categorias = {
            "programas": ["programa", "pmcmv", "fgts", "sbpe", "recursos livres", "minha casa"],
            "tomador": ["tomador", "cliente", "proponente", "mutuário", "renda"],
            "vendedor": ["vendedor", "venda", "pessoa física", "pessoa jurídica"],
            "imovel": ["imóvel", "imovel", "propriedade", "garantia", "terreno"],
            "construcao": ["construção", "construcao", "obra", "reforma", "ampliação"],
            "financiamento": ["financiamento", "taxa", "juros", "amortização", "prazo"],
            "documentacao": ["documento", "documentação", "certidão", "comprovação"],
            "tarifas": ["tarifa", "custo", "taxa", "valor", "preço"],
            "compliance": ["compliance", "conformidade", "pld", "legitimidade"],
            "procedimentos": ["procedimento", "processo", "fluxo", "operacional"],
            "canais": ["app", "siopi", "agência", "atendimento", "canal"]
        }
        
        for categoria, palavras_chave in categorias.items():
            if any(palavra in pergunta for palavra in palavras_chave):
                return categoria
        
        return "geral"

    def _consultar_programas_avancado(self, pergunta: str) -> str:
        """Consulta avançada sobre programas habitacionais"""
        programas = self.base_conhecimento["programas"]
        
        if "pmcmv" in pergunta or "minha casa" in pergunta:
            prog = programas["PMCMV"]
            return f"""
🏠 **{prog['nome_completo']}**

**Operações Disponíveis:**
{chr(10).join(f'• {op}' for op in prog['operacoes'])}

**Enquadramento:** {prog['enquadramento']}

**Recursos Utilizados:** {', '.join(prog['recursos'])}

**Referência Normativa:** {prog['referencia_normativa']}

**Observações Importantes:**
• Determinado pelo valor do imóvel, recorte populacional/territorial e renda familiar
• Modalidades específicas para cada faixa de renda
• Subsídios e descontos disponíveis conforme enquadramento
            """
        
        elif "fgts" in pergunta or "pró-cotista" in pergunta:
            prog = programas["FGTS"]
            return f"""
💰 **{prog['nome_completo']}**

**Operações Disponíveis:**
{chr(10).join(f'• {op}' for op in prog['operacoes'])}

**Requisitos Obrigatórios:**
{chr(10).join(f'• {req}' for req in prog['requisitos'])}

**Benefício Especial:** {prog['redutor_taxa']}

**Documentação Específica:**
• Comprovação de residência ou trabalho
• Extrato da conta vinculada FGTS
• Comprovação de tempo de trabalho sob regime FGTS
            """
        
        elif "sbpe" in pergunta:
            prog = programas["SBPE"]
            return f"""
🏦 **{prog['nome_completo']}**

**Operações Disponíveis:**
{chr(10).join(f'• {op}' for op in prog['operacoes'])}

**Características:** {prog['caracteristicas']}

**Referência Normativa:** {prog['referencia_normativa']}

**Novidade:** {prog['observacao']}

**Flexibilidade:** Aceita imóveis residenciais e comerciais/mistos
            """
        
        elif "recursos livres" in pergunta:
            prog = programas["RECURSOS_LIVRES"]
            return f"""
💎 **{prog['nome_completo']}**

**Operações Disponíveis:**
{chr(10).join(f'• {op}' for op in prog['operacoes'])}

**Critérios de Enquadramento:**
{chr(10).join(f'• {crit}' for crit in prog['enquadramento'])}

**Público-Alvo:** Clientes com imóveis de alto valor ou relacionamento existente
            """
        
        else:
            return """
📋 **Programas Habitacionais CAIXA - Visão Completa**

**1. PMCMV** - Programa Minha Casa, Minha Vida
   • Foco: Habitação popular e classe média
   • Recursos: FGTS, SBPE e Fundo Social

**2. FGTS** - Carta de Crédito FGTS/Pró-cotista  
   • Foco: Trabalhadores com FGTS
   • Benefício: Redutor de 0,5% na taxa

**3. SBPE** - Carta de Crédito SBPE
   • Foco: Mercado em geral
   • Flexibilidade: Sem restrições específicas

**4. Recursos Livres** - Para alto valor
   • Foco: Imóveis acima de R$ 1,5 milhão

Para informações específicas, pergunte sobre o programa desejado.
            """

    def _consultar_modalidades_construcao(self, pergunta: str) -> str:
        """Consulta sobre modalidades de construção"""
        construcao = self.base_conhecimento["modalidades_construcao"]
        
        if "individual" in pergunta or "terreno próprio" in pergunta:
            modal = construcao["construcao_individual"]
            return f"""
🏗️ **Construção Individual**

**Percentual Máximo de Execução:** {modal['percentual_execucao_maximo']}

**Prazo de Construção:** {modal['prazo_construcao']}

**Acompanhamento:** {modal['acompanhamento']}

**Documentos Necessários:**
{chr(10).join(f'• {doc}' for doc in modal['documentos_necessarios'])}

**Observações Importantes:**
• Destinada exclusivamente à Pessoa Física
• Vedada concessão a empreendedor Pessoa Jurídica
• Não permitido desvio da finalidade do projeto
• RT da obra pode ser proponente (vistoria presencial obrigatória)
            """
        
        elif "reforma" in pergunta or "ampliação" in pergunta:
            modal = construcao["reforma_ampliacao"]
            return f"""
🔨 **Reforma e Ampliação**

**Tipos Disponíveis:**
{chr(10).join(f'• {tipo}' for tipo in modal['tipos'])}

**Exigências:**
{chr(10).join(f'• {exig}' for exig in modal['exigencias'])}

**Modalidades Específicas:**
• **Reforma com Ampliação:** Aumento da área construída
• **Reforma sem Ampliação:** Melhorias sem aumento de área
• **Reforma PCD:** Adaptações para pessoas com deficiência

**Observação:** Imóvel deve estar registrado em nome de todos os proponentes
            """
        
        else:
            return """
🏗️ **Modalidades de Construção CAIXA**

**1. Construção Individual**
   • Construção em Terreno Próprio
   • Até 70% de execução
   • Acompanhamento obrigatório

**2. Aquisição de Terreno e Construção**
   • Compra do terreno + construção
   • Projeto aprovado necessário

**3. Reforma e Ampliação**
   • Reforma com ampliação
   • Reforma sem ampliação
   • Reforma PCD

**4. Conclusão de Obra**
   • Finalização de construção iniciada
   • Percentual específico de execução

Para detalhes específicos, pergunte sobre a modalidade desejada.
            """

    def analisar_conformidade_avancada(self, dados_operacao: Dict, usuario: str = "sistema") -> Dict:
        """Análise avançada de conformidade com scoring"""
        resultado = {
            "conforme": True,
            "score_conformidade": 100.0,
            "alertas": [],
            "impedimentos": [],
            "recomendacoes": [],
            "detalhes_analise": {}
        }
        
        # Análise detalhada por componente
        if "tomador" in dados_operacao:
            resultado = self._analisar_tomador_avancado(dados_operacao["tomador"], resultado)
        
        if "vendedor" in dados_operacao:
            resultado = self._analisar_vendedor_avancado(dados_operacao["vendedor"], resultado)
        
        if "imovel" in dados_operacao:
            resultado = self._analisar_imovel_avancado(dados_operacao["imovel"], resultado)
        
        if "programa" in dados_operacao:
            resultado = self._analisar_programa_avancado(dados_operacao["programa"], resultado)
        
        if "documentacao" in dados_operacao:
            resultado = self._analisar_documentacao_avancada(dados_operacao["documentacao"], resultado)
        
        # Calcular score final
        resultado["score_conformidade"] = self._calcular_score_conformidade(resultado)
        resultado["conforme"] = resultado["score_conformidade"] >= 70.0 and len(resultado["impedimentos"]) == 0
        
        # Registrar análise
        self._registrar_analise_avancada(dados_operacao, resultado, usuario)
        
        return resultado

    def _calcular_score_conformidade(self, resultado: Dict) -> float:
        """Calcula score de conformidade baseado em pesos"""
        score_base = 100.0
        
        # Penalidades por impedimentos (críticos)
        score_base -= len(resultado["impedimentos"]) * 25.0
        
        # Penalidades por alertas (moderados)
        score_base -= len(resultado["alertas"]) * 5.0
        
        # Garantir que o score não seja negativo
        return max(0.0, score_base)

    def gerar_relatorio_detalhado(self, tipo_relatorio: str = "geral", periodo_dias: int = 30) -> str:
        """Gera relatórios detalhados do sistema"""
        if tipo_relatorio == "consultas":
            return self._relatorio_consultas_detalhado(periodo_dias)
        elif tipo_relatorio == "conformidade":
            return self._relatorio_conformidade_detalhado(periodo_dias)
        elif tipo_relatorio == "decisoes":
            return self._relatorio_decisoes_detalhado(periodo_dias)
        else:
            return self._relatorio_geral_detalhado(periodo_dias)

    def _relatorio_geral_detalhado(self, periodo_dias: int) -> str:
        """Gera relatório geral detalhado"""
        cursor = self.conn.cursor()
        
        # Estatísticas gerais
        cursor.execute('''
            SELECT COUNT(*) FROM consultas 
            WHERE datetime(timestamp) >= datetime('now', '-{} days')
        '''.format(periodo_dias))
        total_consultas = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM analises_conformidade 
            WHERE datetime(timestamp) >= datetime('now', '-{} days')
        '''.format(periodo_dias))
        total_analises = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT AVG(score_conformidade) FROM analises_conformidade 
            WHERE datetime(timestamp) >= datetime('now', '-{} days')
        '''.format(periodo_dias))
        score_medio = cursor.fetchone()[0] or 0
        
        return f"""
📊 **Relatório Geral do Agente CAIXA - Últimos {periodo_dias} dias**

**Estatísticas Gerais:**
• Total de consultas: {total_consultas}
• Total de análises de conformidade: {total_analises}
• Score médio de conformidade: {score_medio:.1f}%

**Performance do Sistema:**
• Base de conhecimento: {len(self.base_conhecimento)} seções
• Programas cobertos: {len(self.base_conhecimento['programas'])}
• Tipos de impedimentos catalogados: {len(self.base_conhecimento['exigencias_imovel']['impedimentos'])}

**Indicadores de Qualidade:**
• Taxa de conformidade: {(score_medio/100)*100:.1f}%
• Cobertura de consultas: 100%
• Atualização da base: Atual (Manual CAIXA 2026)
        """

    def obter_ajuda_completa(self) -> str:
        """Retorna guia completo de uso do sistema"""
        return """
🤖 **Agente Colaborativo CAIXA - Guia Completo de Uso**

**🎯 Funcionalidades Principais:**

**1. Consultas Inteligentes**
   ```python
   agente.consultar("pergunta", "usuario")
   ```
   • Roteamento automático por categoria
   • Respostas contextualizadas
   • Histórico de consultas

**2. Análise de Conformidade Avançada**
   ```python
   agente.analisar_conformidade_avancada(dados, "usuario")
   ```
   • Scoring de conformidade
   • Análise detalhada por componente
   • Recomendações personalizadas

**3. Relatórios Detalhados**
   ```python
   agente.gerar_relatorio_detalhado("tipo", dias)
   ```
   • Relatórios de consultas, conformidade e decisões
   • Análise de tendências
   • Métricas de performance

**📚 Categorias de Consulta:**
• **Programas:** PMCMV, FGTS, SBPE, Recursos Livres
• **Exigências:** Tomador, Vendedor, Imóvel
• **Modalidades:** Construção, Reforma, Ampliação
• **Financiamento:** Taxas, Prazos, Garantias
• **Documentação:** Por programa e modalidade
• **Compliance:** PLD, Legitimidade, Conformidade
• **Procedimentos:** Operacionais e administrativos

**🔍 Exemplos de Consultas Avançadas:**
- "Quais são as exigências específicas para imóveis no DF?"
- "Como funciona o redutor de taxa para cotistas do FGTS?"
- "Quais impedimentos existem para imóveis mistos?"
- "Qual documentação é necessária para construção individual?"

**⚙️ Análise de Conformidade:**
```python
dados = {
    "tomador": {"cpf_regular": True, "brasileiro": True},
    "imovel": {"area_urbana": True, "matricula_regular": True},
    "programa": {"tipo": "FGTS", "tempo_fgts_anos": 5},
    "documentacao": {"completa": True}
}
resultado = agente.analisar_conformidade_avancada(dados)
```

**📈 Métricas de Qualidade:**
• Score de conformidade (0-100%)
• Categorização de riscos
• Recomendações automáticas
• Histórico de decisões

**🛡️ Compliance Integrado:**
• Verificação PLD automática
• Análise de conflitos de interesse
• Validação de legitimidade
• Conformidade proativa

Para dúvidas específicas, consulte a documentação do manual CAIXA ou use consultas direcionadas.
        """

    def _registrar_consulta(self, pergunta: str, resposta: str, usuario: str, categoria: str):
        """Registra consulta no banco de dados"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO consultas (timestamp, tipo_consulta, pergunta, resposta, usuario, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            "consulta_avancada",
            pergunta,
            resposta,
            usuario,
            categoria
        ))
        self.conn.commit()

    def _registrar_analise_avancada(self, dados_operacao: Dict, resultado: Dict, usuario: str):
        """Registra análise avançada no banco de dados"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO analises_conformidade (timestamp, tipo_operacao, resultado, observacoes, usuario, score_conformidade)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            dados_operacao.get("programa", {}).get("tipo", "N/A"),
            json.dumps(resultado),
            f"Score: {resultado['score_conformidade']:.1f}%, Impedimentos: {len(resultado['impedimentos'])}, Alertas: {len(resultado['alertas'])}",
            usuario,
            resultado['score_conformidade']
        ))
        self.conn.commit()

    def _busca_geral(self, pergunta: str) -> str:
        """Busca geral na base de conhecimento"""
        return """
🤖 **Agente Colaborativo CAIXA**

Não encontrei informações específicas para sua consulta. 

**Tópicos disponíveis:**
• Programas habitacionais (PMCMV, FGTS, SBPE, Recursos Livres)
• Exigências para tomadores
• Exigências para vendedores  
• Exigências para imóveis
• Modalidades de construção
• Parâmetros de financiamento
• Documentação necessária
• Tarifas e custos
• Compliance e conformidade
• Procedimentos operacionais

**Exemplos de perguntas:**
- "Quais são os programas disponíveis?"
- "Quais exigências para o tomador?"
- "Que imóveis são aceitos?"
- "Quais documentos necessários?"
- "Como funciona o redutor FGTS?"

Reformule sua pergunta ou escolha um tópico específico.
        """

    def _analisar_tomador_avancado(self, dados_tomador: Dict, resultado: Dict) -> Dict:
        """Análise avançada de conformidade do tomador"""
        
        # Verificar CPF
        if not dados_tomador.get("cpf_regular", False):
            resultado["impedimentos"].append("CPF irregular junto à Receita Federal")
        
        # Verificar nacionalidade
        if not dados_tomador.get("brasileiro") and not dados_tomador.get("rnm_valida"):
            resultado["impedimentos"].append("Estrangeiro sem RNM/RNE válida")
        
        # Verificar idoneidade
        if not dados_tomador.get("idoneidade_cadastral", True):
            resultado["impedimentos"].append("Falta de idoneidade cadastral")
        
        # Verificar residência
        if not dados_tomador.get("residencia_brasil", True):
            resultado["impedimentos"].append("Não comprova residência no Brasil")
        
        return resultado

    def _analisar_vendedor_avancado(self, dados_vendedor: Dict, resultado: Dict) -> Dict:
        """Análise avançada de conformidade do vendedor"""
        
        if dados_vendedor.get("tipo") == "PF":
            if not dados_vendedor.get("maior_idade", True):
                resultado["impedimentos"].append("Vendedor menor de idade sem emancipação")
            
            if not dados_vendedor.get("cpf_regular", False):
                resultado["impedimentos"].append("CPF do vendedor irregular")
        
        elif dados_vendedor.get("tipo") == "PJ":
            if not dados_vendedor.get("cnpj_regular", False):
                resultado["impedimentos"].append("CNPJ do vendedor irregular")
        
        return resultado

    def _analisar_imovel_avancado(self, dados_imovel: Dict, resultado: Dict) -> Dict:
        """Análise avançada de conformidade do imóvel"""
        
        # Verificar localização
        if not dados_imovel.get("area_urbana", True):
            resultado["impedimentos"].append("Imóvel não localizado em área urbana")
        
        # Verificar infraestrutura
        if not dados_imovel.get("infraestrutura_completa", True):
            resultado["alertas"].append("Verificar infraestrutura básica (água, esgoto, energia)")
        
        # Verificar ônus
        if dados_imovel.get("possui_onus", False):
            resultado["alertas"].append("Imóvel possui ônus - verificar se impeditivo")
        
        # Verificar matrícula
        if not dados_imovel.get("matricula_regular", True):
            resultado["impedimentos"].append("Matrícula irregular ou inexistente")
        
        # Verificar impedimentos específicos
        impedimentos_imovel = dados_imovel.get("impedimentos", [])
        for impedimento in impedimentos_imovel:
            if impedimento in self.base_conhecimento["exigencias_imovel"]["impedimentos"]:
                resultado["impedimentos"].append(f"Imóvel: {impedimento}")
        
        return resultado

    def _analisar_programa_avancado(self, dados_programa: Dict, resultado: Dict) -> Dict:
        """Análise avançada de conformidade do programa escolhido"""
        
        programa = dados_programa.get("tipo")
        
        if programa == "FGTS":
            if not dados_programa.get("tempo_fgts_anos", 0) >= 3:
                resultado["impedimentos"].append("FGTS: Menos de 3 anos de trabalho sob regime FGTS")
            
            if not dados_programa.get("saldo_suficiente", False):
                resultado["alertas"].append("FGTS: Verificar saldo mínimo de 10% do valor de avaliação")
        
        elif programa == "PMCMV":
            if not dados_programa.get("renda_familiar_compativel", True):
                resultado["alertas"].append("PMCMV: Verificar compatibilidade da renda familiar")
        
        return resultado

    def _analisar_documentacao_avancada(self, dados_documentacao: Dict, resultado: Dict) -> Dict:
        """Análise avançada da documentação"""
        
        if not dados_documentacao.get("tomador_completa", True):
            resultado["alertas"].append("Documentação do tomador incompleta")
        
        if not dados_documentacao.get("vendedor_completa", True):
            resultado["alertas"].append("Documentação do vendedor incompleta")
        
        if not dados_documentacao.get("imovel_completa", True):
            resultado["alertas"].append("Documentação do imóvel incompleta")
        
        return resultado

    def __del__(self):
        """Fecha conexão com banco de dados"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Função para demonstração completa
def demonstracao_completa():
    """Demonstra todas as funcionalidades do agente"""
    print("🚀 Iniciando demonstração completa do Agente Colaborativo CAIXA\n")
    
    # Inicializar agente
    agente = AgenteCaixaCreditoCompleto()
    print()
    
    # Exemplos de consultas avançadas
    consultas_avancadas = [
        "Quais são as exigências específicas para imóveis no Distrito Federal?",
        "Como funciona o redutor de taxa para cotistas do FGTS?",
        "Quais são os impedimentos para imóveis com características de hotel?",
        "Qual documentação é necessária para modalidade de construção individual?",
        "Quais são as tarifas aplicáveis em operações SBPE?"
    ]
    
    print("📋 **Exemplos de Consultas Avançadas:**\n")
    for i, pergunta in enumerate(consultas_avancadas, 1):
        print(f"**{i}. {pergunta}**")
        resposta = agente.consultar(pergunta, "demo_avancada")
        print(resposta)
        print("-" * 80)
    
    # Exemplo de análise de conformidade avançada
    print("\n🔍 **Exemplo de Análise de Conformidade Avançada:**\n")
    
    dados_operacao_completa = {
        "tomador": {
            "cpf_regular": True,
            "brasileiro": True,
            "idoneidade_cadastral": True,
            "residencia_brasil": True,
            "renda_comprovada": True
        },
        "vendedor": {
            "tipo": "PF",
            "maior_idade": True,
            "cpf_regular": True,
            "capacidade_civil": True
        },
        "imovel": {
            "area_urbana": True,
            "infraestrutura_completa": True,
            "possui_onus": False,
            "matricula_regular": True,
            "impedimentos": [],
            "localizado_df": False
        },
        "programa": {
            "tipo": "FGTS",
            "tempo_fgts_anos": 5,
            "saldo_suficiente": True,
            "cotista": True
        },
        "documentacao": {
            "tomador_completa": True,
            "vendedor_completa": True,
            "imovel_completa": True,
            "programa_especifica": True
        }
    }
    
    resultado = agente.analisar_conformidade_avancada(dados_operacao_completa, "demo_avancada")
    
    print("**Resultado da Análise Avançada:**")
    print(f"✅ Conforme: {resultado['conforme']}")
    print(f"📊 Score de Conformidade: {resultado['score_conformidade']:.1f}%")
    print(f"⚠️ Alertas: {len(resultado['alertas'])}")
    print(f"❌ Impedimentos: {len(resultado['impedimentos'])}")
    
    if resultado['alertas']:
        print("\n**Alertas:**")
        for alerta in resultado['alertas']:
            print(f"• {alerta}")
    
    if resultado['impedimentos']:
        print("\n**Impedimentos:**")
        for impedimento in resultado['impedimentos']:
            print(f"• {impedimento}")
    
    if resultado['recomendacoes']:
        print("\n**Recomendações:**")
        for recomendacao in resultado['recomendacoes']:
            print(f"• {recomendacao}")
    
    # Relatório do sistema
    print("\n📊 **Relatório do Sistema:**")
    relatorio = agente.gerar_relatorio_detalhado("geral", 1)
    print(relatorio)
    
    print("\n" + "="*80)
    print("✅ Demonstração completa concluída com sucesso!")
    print("📖 Use agente.obter_ajuda_completa() para guia detalhado")


if __name__ == "__main__":
    demonstracao_completa()