def get_base_css():
    """
    Retorna a string CSS base para estilização do PDF.
    Não inclui o conteúdo do cabeçalho dinâmico.
    """
    return """
@page {
    size: A4;
    margin: 2cm;
    /* O conteúdo do cabeçalho será injetado aqui via uma função ou template */
}
    
body {
    font-family: 'Segoe UI', sans-serif;
    font-size: 10.5px;
    color: #111;
    line-height: 1.5;
}
    
h1 {
    font-size: 18px;
    color: #1a4e8a;
    border-bottom: 1px solid #ccc;
    margin-top: 24px;
}
    
h2 {
    font-size: 16px;
    color: #1a4e8a;
    margin-top: 20px;
}
    
h3 {
    font-size: 14px;
    color: #444;
    margin-top: 16px;
}
    
pre, code {
    font-family: "Roboto Mono", monospace;
    font-size: 9px;
    white-space: pre;
    overflow-x: auto;
    background: #f5f5f5;
    padding: 6px 8px;
    border-left: 3px solid #1a4e8a;
    border-radius: 4px;
    margin: 8px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9.5px;
    margin: 10px 0;
}
    
th, td {
    border: 1px solid #ccc;
    padding: 4px 6px;
    text-align: left;
}
    
th {
    background: #f0f0f0;
}
"""

def generate_pdf_css(header_text: str = "Documentação"):
    """
    Gera a string CSS completa para o PDF, incluindo o conteúdo dinâmico do cabeçalho.

    Args:
        header_text (str): O texto a ser exibido no cabeçalho superior central de cada página.

    Returns:
        str: A string CSS completa.
    """
    base_css = get_base_css()
    
    # Injetar o cabeçalho no CSS base.
    # O conteúdo precisa ser uma string literal escapada para ser válida no CSS.
    escaped_header_text = header_text.replace('"', '\\"')
    header_section = f"""
    @top-center {{
        content: "{escaped_header_text}\"; /* Escapa aspas duplas no texto */
        font-size: 10px;
        font-style: italic;
        color: #555;
    }}
    """
    
    # Encontra a posição ideal para injetar o header_section dentro de @page
    # Uma forma simples é usar replace, mas uma solução mais robusta pode ser necessária
    # se o CSS base mudar muito ou se houver múltiplos @page blocks.
    # Por enquanto, vamos assumir que queremos injetar dentro do primeiro @page block.
    # Para simplicidade, vamos injetar no final do @page, antes de fechar a chave.
    
    # Encontra a posição do '}' que fecha o @page para injetar o header_section antes dele.
    # Isso é um pouco "frágil" e depende da estrutura do CSS base.
    # Uma alternativa mais robusta seria usar um motor de template como Jinja2 para o próprio CSS.
    
    # Exemplo simples, buscando e substituindo a marca de fechamento do @page
    # que está no get_base_css. Vamos adicionar um placeholder para ser mais seguro.

    # Nova estratégia: usar um placeholder no base_css
    base_css_with_placeholder = """
@page {
    size: A4;
    margin: 2cm;
    {HEADER_PLACEHOLDER}
}
    
body {
    font-family: 'Segoe UI', sans-serif;
    font-size: 10.5px;
    color: #111;
    line-height: 1.5;
}
    
h1 {
    font-size: 18px;
    color: #1a4e8a;
    border-bottom: 1px solid #ccc;
    margin-top: 24px;
}
    
h2 {
    font-size: 16px;
    color: #1a4e8a;
    margin-top: 20px;
}
    
h3 {
    font-size: 14px;
    color: #444;
    margin-top: 16px;
}
    
pre, code {
    font-family: "Roboto Mono", monospace;
    font-size: 9px;
    white-space: pre;
    overflow-x: auto;
    background: #f5f5f5;
    padding: 6px 8px;
    border-left: 3px solid #1a4e8a;
    border-radius: 4px;
    margin: 8px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9.5px;
    margin: 10px 0;
}
    
th, td {
    border: 1px solid #ccc;
    padding: 4px 6px;
    text-align: left;
}
    
th {
    background: #f0f0f0;
}
"""
    final_css = base_css_with_placeholder.replace("{HEADER_PLACEHOLDER}", header_section)
    return final_css

# Teste rápido (pode ser removido após verificar)
if __name__ == "__main__":
    test_css = generate_pdf_css("Minha Documentação Personalizada")
    print(test_css)

    test_css_with_quotes = generate_pdf_css('Documentação com "Aspas" e Barras \\ Invertidas')
    print("\n--- CSS com aspas ---")
    print(test_css_with_quotes)