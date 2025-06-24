from markdown2 import markdown
from weasyprint import HTML, CSS
from os import path

class MarkdownToPDFConverter:
    """
    Converte um arquivo Markdown para PDF usando markdown2 e WeasyPrint.
    """
    def __init__(self, md_path: str, pdf_path: str, custom_css_string: str = ""):
        """
        Inicializa o conversor.

        Args:
            md_path (str): Caminho para o arquivo Markdown de entrada.
            pdf_path (str): Caminho para o arquivo PDF de saída.
            custom_css_string (str, optional): String CSS a ser aplicada.
                                               Se não fornecida, espera-se que o CSS seja tratado externamente.
        """
        if not path.exists(md_path):
            raise FileNotFoundError(f"Arquivo Markdown não encontrado: {md_path}")
        
        self.md_path = md_path
        self.pdf_path = pdf_path
        self.custom_css_string = custom_css_string

    def convert(self):
        """
        Executa a conversão do Markdown para PDF.
        """
        print(f"Iniciando conversão de '{self.md_path}' para '{self.pdf_path}'...")
        try:
            with open(self.md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            html_content = markdown(md_content, extras=["fenced-code-blocks", "tables", "code-friendly"])

            stylesheets = []
            if self.custom_css_string:
                stylesheets.append(CSS(string=self.custom_css_string))
            
            HTML(string=html_content).write_pdf(self.pdf_path, stylesheets=stylesheets)
            print(f"PDF gerado com sucesso em: {self.pdf_path}")
            return self.pdf_path
        except FileNotFoundError:
            print(f"Erro: O arquivo de entrada Markdown '{self.md_path}' não foi encontrado.")
            raise
        except Exception as e:
            print(f"Ocorreu um erro inesperado durante a conversão: {e}")
            raise