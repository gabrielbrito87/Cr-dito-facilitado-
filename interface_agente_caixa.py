#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Web do Agente Colaborativo CAIXA
Sistema completo de consultas e análise de conformidade
"""

import streamlit as st
import json
import sqlite3
from datetime import datetime
from agente_caixa_completo import AgenteCaixaCreditoCompleto

# Configuração da página
st.set_page_config(
    page_title="Agente Colaborativo CAIXA",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e6da4 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .alert-success {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    .alert-warning {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
    }
    .alert-danger {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar agente
@st.cache_resource
def init_agente():
    return AgenteCaixaCreditoCompleto()

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Agente Colaborativo CAIXA</h1>
        <p>Sistema Inteligente de Consultas e Análise de Conformidade para Crédito Imobiliário</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar agente
    agente = init_agente()
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Caixa_Econ%C3%B4mica_Federal_logo.svg/1200px-Caixa_Econ%C3%B4mica_Federal_logo.svg.png", width=200)
        
        st.markdown("### 🎯 Funcionalidades")
        opcao = st.selectbox(
            "Escolha uma funcionalidade:",
            [
                "🔍 Consultas Inteligentes",
                "📊 Análise de Conformidade",
                "📈 Relatórios e Métricas",
                "📚 Base de Conhecimento",
                "🛠️ Ferramentas Avançadas"
            ]
        )
        
        st.markdown("### 👤 Usuário")
        usuario = st.text_input("Nome do usuário:", value="Analista")
        
        st.markdown("### ℹ️ Informações")
        st.info(f"""
        **Versão:** {agente.versao}
        **Base:** Manual CAIXA 2026
        **Programas:** {len(agente.base_conhecimento['programas'])}
        **Status:** ✅ Ativo
        """)
    
    # Conteúdo principal baseado na opção selecionada
    if opcao == "🔍 Consultas Inteligentes":
        consultas_inteligentes(agente, usuario)
    elif opcao == "📊 Análise de Conformidade":
        analise_conformidade(agente, usuario)
    elif opcao == "📈 Relatórios e Métricas":
        relatorios_metricas(agente)
    elif opcao == "📚 Base de Conhecimento":
        base_conhecimento(agente)
    elif opcao == "🛠️ Ferramentas Avançadas":
        ferramentas_avancadas(agente, usuario)

def consultas_inteligentes(agente, usuario):
    st.header("🔍 Consultas Inteligentes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h4>💡 Como usar</h4>
            <p>Digite sua pergunta sobre crédito imobiliário CAIXA. O sistema identifica automaticamente a categoria e fornece respostas precisas baseadas no manual oficial.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Campo de consulta
        pergunta = st.text_area(
            "Digite sua pergunta:",
            placeholder="Ex: Quais são as exigências para imóveis no Distrito Federal?",
            height=100
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            consultar = st.button("🔍 Consultar", type="primary")
        with col_btn2:
            limpar = st.button("🗑️ Limpar")
        
        if limpar:
            st.rerun()
        
        if consultar and pergunta:
            with st.spinner("Processando consulta..."):
                resposta = agente.consultar(pergunta, usuario)
                
                st.markdown("### 📋 Resposta")
                st.markdown(f"""
                <div class="alert-success">
                    {resposta.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Exemplos de Consultas")
        
        exemplos = [
            "Quais são os programas habitacionais disponíveis?",
            "Quais exigências para o tomador?",
            "Que imóveis são aceitos como garantia?",
            "Como funciona o redutor FGTS?",
            "Quais documentos para construção individual?",
            "Quais são as tarifas aplicáveis?",
            "Como funciona a conformidade proativa?",
            "Quais impedimentos para imóveis?"
        ]
        
        for exemplo in exemplos:
            if st.button(f"💬 {exemplo}", key=f"ex_{hash(exemplo)}"):
                st.session_state.pergunta_exemplo = exemplo
                st.rerun()

def analise_conformidade(agente, usuario):
    st.header("📊 Análise de Conformidade")
    
    st.markdown("""
    <div class="feature-box">
        <h4>🎯 Análise Avançada de Conformidade</h4>
        <p>Sistema de scoring que avalia a conformidade de operações de crédito imobiliário com base no manual CAIXA.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulário de análise
    with st.form("analise_conformidade"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Dados do Tomador")
            cpf_regular = st.checkbox("CPF regular", value=True)
            brasileiro = st.checkbox("Brasileiro nato/naturalizado", value=True)
            idoneidade = st.checkbox("Idoneidade cadastral", value=True)
            residencia_brasil = st.checkbox("Residência no Brasil", value=True)
            
            st.subheader("🏢 Dados do Vendedor")
            tipo_vendedor = st.selectbox("Tipo de vendedor", ["PF", "PJ"])
            vendedor_regular = st.checkbox("Documentação regular", value=True)
            
        with col2:
            st.subheader("🏠 Dados do Imóvel")
            area_urbana = st.checkbox("Localizado em área urbana", value=True)
            infraestrutura = st.checkbox("Infraestrutura completa", value=True)
            matricula_regular = st.checkbox("Matrícula regular", value=True)
            possui_onus = st.checkbox("Possui ônus")
            
            st.subheader("💰 Programa")
            programa = st.selectbox("Programa", ["FGTS", "PMCMV", "SBPE", "RECURSOS_LIVRES"])
            if programa == "FGTS":
                tempo_fgts = st.number_input("Tempo FGTS (anos)", min_value=0, max_value=50, value=5)
                saldo_suficiente = st.checkbox("Saldo suficiente", value=True)
        
        analisar = st.form_submit_button("📊 Analisar Conformidade", type="primary")
    
    if analisar:
        # Preparar dados para análise
        dados_operacao = {
            "tomador": {
                "cpf_regular": cpf_regular,
                "brasileiro": brasileiro,
                "idoneidade_cadastral": idoneidade,
                "residencia_brasil": residencia_brasil
            },
            "vendedor": {
                "tipo": tipo_vendedor,
                "documentacao_regular": vendedor_regular
            },
            "imovel": {
                "area_urbana": area_urbana,
                "infraestrutura_completa": infraestrutura,
                "matricula_regular": matricula_regular,
                "possui_onus": possui_onus
            },
            "programa": {
                "tipo": programa
            }
        }
        
        if programa == "FGTS":
            dados_operacao["programa"]["tempo_fgts_anos"] = tempo_fgts
            dados_operacao["programa"]["saldo_suficiente"] = saldo_suficiente
        
        with st.spinner("Analisando conformidade..."):
            resultado = agente.analisar_conformidade_avancada(dados_operacao, usuario)
        
        # Exibir resultados
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{'✅' if resultado['conforme'] else '❌'}</h3>
                <p><strong>Conformidade</strong></p>
                <p>{'Aprovado' if resultado['conforme'] else 'Reprovado'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            score_color = "success" if resultado['score_conformidade'] >= 80 else "warning" if resultado['score_conformidade'] >= 60 else "danger"
            st.markdown(f"""
            <div class="metric-card">
                <h3>{resultado['score_conformidade']:.1f}%</h3>
                <p><strong>Score</strong></p>
                <p>Conformidade</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(resultado['impedimentos'])}</h3>
                <p><strong>Impedimentos</strong></p>
                <p>{len(resultado['alertas'])} Alertas</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detalhes dos resultados
        if resultado['impedimentos']:
            st.markdown("### ❌ Impedimentos Identificados")
            for impedimento in resultado['impedimentos']:
                st.markdown(f"""
                <div class="alert-danger">
                    <strong>Impedimento:</strong> {impedimento}
                </div>
                """, unsafe_allow_html=True)
        
        if resultado['alertas']:
            st.markdown("### ⚠️ Alertas")
            for alerta in resultado['alertas']:
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>Alerta:</strong> {alerta}
                </div>
                """, unsafe_allow_html=True)
        
        if resultado['recomendacoes']:
            st.markdown("### 💡 Recomendações")
            for recomendacao in resultado['recomendacoes']:
                st.markdown(f"• {recomendacao}")

def relatorios_metricas(agente):
    st.header("📈 Relatórios e Métricas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Relatórios Disponíveis")
        tipo_relatorio = st.selectbox(
            "Tipo de relatório:",
            ["geral", "consultas", "conformidade", "decisoes"]
        )
        
        periodo = st.selectbox(
            "Período:",
            [7, 15, 30, 60, 90],
            index=2
        )
        
        if st.button("📋 Gerar Relatório"):
            with st.spinner("Gerando relatório..."):
                relatorio = agente.gerar_relatorio_detalhado(tipo_relatorio, periodo)
                st.markdown("### 📋 Relatório Gerado")
                st.text(relatorio)
    
    with col2:
        st.subheader("📈 Métricas do Sistema")
        
        # Métricas simuladas (em produção, viriam do banco de dados)
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.metric("Total de Consultas", "1,234", "+12%")
            st.metric("Análises de Conformidade", "567", "+8%")
        
        with col_m2:
            st.metric("Score Médio", "87.3%", "+2.1%")
            st.metric("Taxa de Aprovação", "73.2%", "-1.5%")

def base_conhecimento(agente):
    st.header("📚 Base de Conhecimento")
    
    # Navegação por categorias
    categoria = st.selectbox(
        "Selecione uma categoria:",
        [
            "Programas Habitacionais",
            "Exigências do Tomador",
            "Exigências do Vendedor", 
            "Exigências do Imóvel",
            "Modalidades de Construção",
            "Parâmetros de Financiamento",
            "Tarifas e Custos",
            "Compliance",
            "Procedimentos Operacionais"
        ]
    )
    
    if categoria == "Programas Habitacionais":
        st.subheader("🏠 Programas Habitacionais")
        
        programa_selecionado = st.selectbox(
            "Selecione um programa:",
            list(agente.base_conhecimento["programas"].keys())
        )
        
        programa_info = agente.base_conhecimento["programas"][programa_selecionado]
        
        st.markdown(f"### {programa_info['nome_completo']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Operações Disponíveis:**")
            for operacao in programa_info["operacoes"]:
                st.markdown(f"• {operacao}")
        
        with col2:
            if "enquadramento" in programa_info:
                st.markdown(f"**Enquadramento:** {programa_info['enquadramento']}")
            if "requisitos" in programa_info:
                st.markdown("**Requisitos:**")
                for req in programa_info["requisitos"]:
                    st.markdown(f"• {req}")
    
    elif categoria == "Exigências do Imóvel":
        st.subheader("🏠 Exigências do Imóvel")
        
        tab1, tab2, tab3 = st.tabs(["Requisitos Básicos", "Situações Aceitas", "Impedimentos"])
        
        with tab1:
            st.markdown("**Requisitos Básicos:**")
            for req in agente.base_conhecimento["exigencias_imovel"]["requisitos_basicos"]:
                st.markdown(f"✅ {req}")
        
        with tab2:
            st.markdown("**Situações Aceitas:**")
            for situacao in agente.base_conhecimento["exigencias_imovel"]["situacoes_aceitas"]:
                st.markdown(f"✅ {situacao}")
        
        with tab3:
            st.markdown("**Impedimentos:**")
            for impedimento in agente.base_conhecimento["exigencias_imovel"]["impedimentos"]:
                st.markdown(f"❌ {impedimento}")

def ferramentas_avancadas(agente, usuario):
    st.header("🛠️ Ferramentas Avançadas")
    
    tab1, tab2, tab3 = st.tabs(["Simulador", "Validador", "Exportar"])
    
    with tab1:
        st.subheader("🎯 Simulador de Cenários")
        st.info("Simule diferentes cenários de financiamento e veja o impacto na conformidade.")
        
        # Implementar simulador
        st.markdown("*Funcionalidade em desenvolvimento*")
    
    with tab2:
        st.subheader("✅ Validador de Documentos")
        st.info("Valide se a documentação está completa para cada tipo de operação.")
        
        # Implementar validador
        st.markdown("*Funcionalidade em desenvolvimento*")
    
    with tab3:
        st.subheader("📤 Exportar Dados")
        st.info("Exporte relatórios e análises em diferentes formatos.")
        
        if st.button("📊 Exportar Base de Conhecimento (JSON)"):
            dados_export = json.dumps(agente.base_conhecimento, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 Download JSON",
                data=dados_export,
                file_name="base_conhecimento_caixa.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()