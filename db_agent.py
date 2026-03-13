"""
db_agent.py — Agente Text-to-SQL: consulta banco de dados em linguagem natural.
Use: python db_agent.py [--url URL_DO_BANCO]

Exemplos de perguntas:
  - Quantos registros existem na tabela clientes?
  - Quais os 5 produtos mais vendidos?
  - Qual o faturamento total do mês passado?
"""

import argparse
import logging

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

from core.config import cfg, garantir_pastas

logging.basicConfig(level=logging.WARNING)
console = Console()


def parse_args():
    parser = argparse.ArgumentParser(description="Agente SQL — IA Local RAG")
    parser.add_argument("--url", default=cfg.database_url, help="URL do banco de dados")
    return parser.parse_args()


def criar_agente(database_url: str):
    """Cria o agente SQL conectado ao banco especificado."""
    console.print(f"[dim]Conectando ao banco: {database_url}[/dim]")
    db = SQLDatabase.from_uri(database_url)

    tabelas = db.get_usable_table_names()
    console.print(f"[green]✅ Tabelas disponíveis: {', '.join(tabelas)}[/green]")

    llm = ChatOllama(
        model=cfg.llm_model,
        base_url=cfg.ollama_url,
        temperature=0,  # Zero para consultas SQL — precisão máxima
    )

    agente = create_sql_agent(
        llm=llm,
        db=db,
        verbose=False,
        agent_executor_kwargs={"handle_parsing_errors": True},
        prefix="""Você é um agente SQL especializado. Responda SEMPRE em português do Brasil.
        Gere consultas SQL precisas. Use apenas as tabelas disponíveis.
        Formate números com separadores brasileiros quando aplicável.""",
    )
    return agente


def main():
    garantir_pastas()
    args = parse_args()

    console.print(Panel.fit(
        "[bold blue]🗄️  Agente SQL — Consultas em Linguagem Natural[/bold blue]\n"
        f"Banco: [cyan]{args.url}[/cyan]\n"
        f"Modelo: [cyan]{cfg.llm_model}[/cyan]",
        border_style="blue",
    ))

    try:
        agente = criar_agente(args.url)
    except Exception as exc:
        console.print(f"[bold red]❌ Erro ao conectar ao banco: {exc}[/bold red]")
        return

    console.print("\n[bold]Exemplos de perguntas:[/bold]")
    console.print("  • Quantos registros existem na tabela clientes?")
    console.print("  • Quais são os 5 produtos mais vendidos?")
    console.print("  • Qual o faturamento total?")
    console.print("\nDigite [bold]sair[/bold] para encerrar.\n")

    while True:
        try:
            pergunta = console.input("[bold blue]Pergunta:[/bold blue] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]👋 Encerrando...[/yellow]")
            break

        if not pergunta:
            continue
        if pergunta.lower() in ("sair", "exit", "quit"):
            break

        try:
            with console.status("[dim]🔍 Consultando banco...[/dim]"):
                resposta = agente.invoke({"input": pergunta})

            console.print("\n[bold green]Resposta:[/bold green]")
            console.print(Panel(str(resposta.get("output", resposta)), border_style="green"))
            console.print()

        except Exception as exc:
            console.print(f"[red]❌ Erro: {exc}[/red]")


if __name__ == "__main__":
    main()
