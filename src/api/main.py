from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import os
import secrets
import json

from src.core.converter import MarkdownToPDFConverter
from src.core.styles import generate_pdf_css
from src.core.postman_json_to_markdown import PostmanJsonToMarkdown # NOVO: Importa a nova classe

# ======================================================================# Configuração da Aplicação FastAPI# ======================================================================

app = FastAPI(
    title="Gerador de Documentação de API em PDF",
    description="API para converter documentações Markdown (.md) ou collection Postman (json) em documentos PDF com cabeçalho personalizado.",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "src" / "templates"))

app.mount("/statics", StaticFiles(directory=str(BASE_DIR / "src" / "statics")), name="statics")

TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True) # Garante que o diretório temp existe

# ======================================================================# Endpoints da API# ======================================================================
@app.get("/", response_class=HTMLResponse, summary="Página inicial do conversor")
async def read_root():
    """
    Exibe a página HTML para upload de arquivos Markdown e personalização do cabeçalho.
    """
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/convert/", summary="Converte um arquivo Markdown ou JSON de coleção Postman para PDF")
async def convert_to_pdf(
    markdown_file: UploadFile = File(None),
    postman_json_file: UploadFile = File(None),
    header_text: str = Form("Documentação")
):
    """
    Recebe um arquivo Markdown OU um arquivo JSON de coleção Postman e um texto para o cabeçalho,
    converte para PDF e retorna o arquivo PDF gerado.

    Args:
        markdown_file (UploadFile): O arquivo Markdown (.md) enviado pelo usuário. (Opcional)
        postman_json_file (UploadFile): O arquivo JSON da coleção Postman exportado. (Opcional)
        header_text (str): O texto a ser exibido no cabeçalho superior central do PDF.
                            Valor padrão é "Documentação".

    Returns:
        FileResponse: O arquivo PDF gerado para download.
    """
    input_md_path = None
    output_pdf_path = None
    output_pdf_filename = None

    try:
        if markdown_file and markdown_file.filename:
            if not markdown_file.filename.endswith(('.md', '.markdown')):
                raise HTTPException(
                    status_code=400,
                    detail="Por favor, envie um arquivo Markdown válido (.md ou .markdown)."
                )
            input_md_path = TEMP_DIR / f"{secrets.token_hex(8)}_{markdown_file.filename}"
            output_pdf_filename = f"{Path(markdown_file.filename).stem}.pdf"
            
            with open(input_md_path, "wb") as buffer:
                shutil.copyfileobj(markdown_file.file, buffer)
            
        elif postman_json_file and postman_json_file.filename:
            if not postman_json_file.filename.endswith('.json'):
                raise HTTPException(
                    status_code=400,
                    detail="Por favor, envie um arquivo JSON (.json) válido para a coleção Postman."
                )

            unique_id = secrets.token_hex(8)
            input_md_path = TEMP_DIR / f"postman_doc_{unique_id}.md"
            output_pdf_filename = f"postman_collection_{unique_id}.pdf"

            try:
                json_content = await postman_json_file.read()
                postman_data = json.loads(json_content)
                
                parser = PostmanJsonToMarkdown(postman_data)
                markdown_content = parser.convert_to_markdown()
                
                with open(input_md_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Arquivo JSON do Postman inválido. Verifique a formatação.")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) # Erros de validação da classe PostmanJsonToMarkdown
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo JSON do Postman: {e}")

        else:
            raise HTTPException(
                status_code=400,
                detail="Por favor, envie um arquivo Markdown ou um arquivo JSON de coleção Postman."
            )

        output_pdf_path = TEMP_DIR / output_pdf_filename

        dynamic_css = generate_pdf_css(header_text)

        try:
            converter = MarkdownToPDFConverter(
                md_path=str(input_md_path),
                pdf_path=str(output_pdf_path),
                custom_css_string=dynamic_css
            )
            converter.convert()
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro durante a conversão para PDF: {e}")
        
        return FileResponse(
            path=str(output_pdf_path),
            filename=output_pdf_filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{output_pdf_filename}\""}
        )

    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado no servidor: {e}")
    finally:
        if input_md_path and os.path.exists(input_md_path):
            os.remove(input_md_path)
        if output_pdf_path and os.path.exists(output_pdf_path):
            pass