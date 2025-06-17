# src/core/postman_json_to_markdown.py
import json

class PostmanJsonToMarkdown:
    def __init__(self, postman_collection_json: dict):
        if not isinstance(postman_collection_json, dict) or "item" not in postman_collection_json:
            raise ValueError("O JSON fornecido não parece ser uma coleção Postman válida.")
        self.collection_data = postman_collection_json

    def _format_request_body(self, body_data: dict) -> str:
        """Formata o corpo da requisição para Markdown."""
        if body_data and body_data.get("mode") == "raw" and "raw" in body_data:
            try:
                # Tenta parsear como JSON para formatar bonito
                raw_content = json.loads(body_data["raw"])
                return "```json\n" + json.dumps(raw_content, indent=2) + "\n```"
            except json.JSONDecodeError:
                # Se não for JSON, apenas retorna o texto bruto
                return "```\n" + body_data["raw"] + "\n```"
        return ""

    def _format_response_body(self, response_data: list) -> str:
        """Formata o corpo da primeira resposta para Markdown."""
        if response_data and isinstance(response_data, list) and len(response_data) > 0:
            first_response = response_data[0]
            if "body" in first_response:
                try:
                    # Tenta parsear como JSON para formatar bonito
                    body_content = json.loads(first_response["body"])
                    return "```json\n" + json.dumps(body_content, indent=2) + "\n```"
                except json.JSONDecodeError:
                    # Se não for JSON, apenas retorna o texto bruto
                    return "```\n" + first_response["body"] + "\n```"
        return ""
    
    def _format_parameters(self, params: list, param_type: str) -> str:
        """Formata parâmetros (query, path, header, cookie) para uma tabela Markdown."""
        if not params:
            return ""
        
        md_table = f"#### Parâmetros de {param_type}:\n\n"
        md_table += "| Nome | Valor Exemplo | Descrição |\n"
        md_table += "|---|---|---|\n"
        
        for param in params:
            name = param.get('key', param.get('name', ''))
            value = param.get('value', '')
            description = param.get('description', '').replace('\n', ' ').strip() # Remove quebras de linha
            md_table += f"| `{name}` | `{value}` | {description} |\n"
        md_table += "\n"
        return md_table

    def convert_to_markdown(self) -> str:
        """
        Converte os dados da coleção Postman (JSON) para uma string Markdown.
        """
        collection = self.collection_data
        
        markdown_output = f"# {collection.get('info', {}).get('name', 'Documentação da API')}\n\n"
        
        description = collection.get('info', {}).get('description', '')
        if description:
            markdown_output += f"{description}\n\n"

        # Função auxiliar para processar itens recursivamente (pastas e requisições)
        def process_items(items, level=2):
            nonlocal markdown_output
            for item in items:
                if "item" in item: # É uma pasta (folder)
                    markdown_output += f"{'#' * level} {item['name']}\n\n"
                    if item.get('description'):
                        markdown_output += f"{item['description']}\n\n"
                    process_items(item["item"], level + 1)
                elif "request" in item: # É uma requisição (request)
                    markdown_output += f"{'#' * level} {item.get('name', 'Endpoint sem nome')}\n\n"
                    
                    request = item.get('request', {})
                    if request.get('description'):
                        markdown_output += f"{request['description']}\n\n"
                    
                    markdown_output += f"**Método:** `{request.get('method', 'GET')}`\n"
                    
                    # Tenta obter a URL formatada
                    url_raw = request.get('url', {}).get('raw', '')
                    if url_raw:
                        markdown_output += f"**URL:** `{url_raw}`\n\n"
                    
                    # Parâmetros de Query, Path, Header, Cookie
                    if request.get('url', {}).get('query'):
                        markdown_output += self._format_parameters(request['url']['query'], 'Query')
                    if request.get('url', {}).get('variable'): # Path variables
                        markdown_output += self._format_parameters(request['url']['variable'], 'Path')
                    if request.get('header'):
                        markdown_output += self._format_parameters(request['header'], 'Header')
                    if request.get('cookie'):
                        markdown_output += self._format_parameters(request['cookie'], 'Cookie')


                    # Exemplo de Requisição (Body)
                    request_body_md = self._format_request_body(request.get('body'))
                    if request_body_md:
                        markdown_output += "### Corpo da Requisição:\n"
                        markdown_output += request_body_md + "\n\n"

                    # Exemplo de Resposta
                    response_body_md = self._format_response_body(item.get('response'))
                    if response_body_md:
                        markdown_output += "### Exemplo de Resposta:\n"
                        markdown_output += response_body_md + "\n\n"
        
        process_items(collection.get("item", []))
        
        return markdown_output

if __name__ == '__main__':
    # Este é um exemplo de como você pode usar a classe
    # Simula um JSON de coleção Postman (recorte simplificado)
    sample_postman_json = {
        "info": {
            "name": "Minha API de Teste (JSON)",
            "description": "Uma coleção de exemplo para testar a conversão de JSON para Markdown."
        },
        "item": [
            {
                "name": "Auth",
                "item": [
                    {
                        "name": "Login User",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json", "description": "Tipo de conteúdo"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": "{\n    \"username\": \"testuser\",\n    \"password\": \"password123\"\n}"
                            },
                            "url": {
                                "raw": "https://api.example.com/login",
                                "protocol": "https",
                                "host": ["api", "example", "com"],
                                "path": ["login"]
                            },
                            "description": "Autentica um usuário e retorna um token."
                        },
                        "response": [
                            {
                                "name": "Successful Login",
                                "status": "OK",
                                "code": 200,
                                "body": "{\n    \"token\": \"abc.def.ghi\",\n    \"expiresIn\": 3600\n}"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Produtos",
                "item": [
                    {
                        "name": "Get Product by ID",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "https://api.example.com/products/:productId",
                                "protocol": "https",
                                "host": ["api", "example", "com"],
                                "path": ["products", ":productId"],
                                "query": [
                                    {"key": "includeDetails", "value": "true", "description": "Incluir detalhes adicionais do produto."}
                                ],
                                "variable": [
                                    {"key": "productId", "value": "123", "description": "ID do produto a ser buscado."}
                                ]
                            },
                            "description": "Retorna os detalhes de um produto específico."
                        },
                        "response": [
                            {
                                "name": "Product Details",
                                "status": "OK",
                                "code": 200,
                                "body": "{\n    \"id\": \"123\",\n    \"name\": \"Smartwatch\",\n    \"price\": 299.99,\n    \"currency\": \"BRL\"\n}"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    try:
        parser = PostmanJsonToMarkdown(sample_postman_json)
        markdown_doc = parser.convert_to_markdown()
        
        # Salva o Markdown gerado para visualização
        with open("postman_json_doc.md", "w", encoding="utf-8") as f:
            f.write(markdown_doc)
        print("Documentação Markdown do Postman JSON gerada com sucesso em postman_json_doc.md")
        
    except Exception as e:
        print(f"Erro: {e}")