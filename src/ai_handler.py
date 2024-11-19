import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

class AIHandler:
    def __init__(self):
        self.xai_key = os.getenv('X_AI_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        
        self.models = {
            "Llama-3-8B": {
                "api_base": "https://openrouter.ai/api/v1/chat/completions",
                "model": "meta-llama/llama-3-8b-instruct",
                "headers": {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                }
            },
            "Llama-3-70B": {
                "api_base": "https://openrouter.ai/api/v1/chat/completions",
                "model": "meta-llama/llama-3-70b-instruct",
                "headers": {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                }
            },
            "X.AI Grok": {
                "api_base": "https://api.x.ai/v1/chat/completions",
                "model": "grok-beta",
                "headers": {
                    "Authorization": f"Bearer {self.xai_key}",
                    "Content-Type": "application/json"
                }
            }
        }

        self.citation_styles = {
            "APA": "Genera las referencias bibliográficas en formato APA (7ma edición)",
            "IEEE": "Genera las referencias bibliográficas en formato IEEE",
            "Vancouver": "Genera las referencias bibliográficas en formato Vancouver",
            "Chicago": "Genera las referencias bibliográficas en formato Chicago",
            "MLA": "Genera las referencias bibliográficas en formato MLA"
        }
    
    def generate_response(self, system_prompt: str, user_prompt: str, content: Dict[str, str], model_name: str = "Llama-3-8B") -> str:
        model_config = self.models[model_name]
        
        enhanced_system_prompt = f"""
        {system_prompt}
        IMPORTANTE: Utiliza ÚNICAMENTE la información proporcionada en los documentos de referencia.
        Para cada afirmación o dato, debes indicar explícitamente entre corchetes de qué documento proviene, por ejemplo: [Documento: nombre_archivo.pdf]
        No agregues información externa ni conocimiento general que no esté en los documentos proporcionados.
        """
        
        payload = {
            "messages": [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": model_config["model"],
            "stream": False,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                model_config["api_base"],
                headers=model_config["headers"],
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"Error en la llamada a la API: {str(e)}")
    
    def generate_article_section(self, content: Dict[str, str], title: str, section_type: str, custom_prompt: str, model_name: str) -> Dict[str, str]:
        system_prompts = {
            "resumen": """Eres un experto en redacción académica. Genera un resumen conciso y bien estructurado.
                         Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf].""",
            "introduccion": """Eres un experto en redacción académica. Genera una introducción que contextualice el tema y presente los objetivos.
                             Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf].""",
            "metodologia": """Eres un experto en redacción académica. Describe la metodología utilizada.
                            Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf].""",
            "resultados": """Eres un experto en redacción académica. Presenta los resultados principales.
                           Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf].""",
            "conclusiones": """Eres un experto en redacción académica. Genera conclusiones sólidas.
                             Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf].""",
            "discusion": """Eres un experto en redacción académica. Genera una discusión que analice los resultados.
                          Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf]."""
        }
        
        system_prompt = custom_prompt if custom_prompt else system_prompts[section_type]
        
        prompt = f"""Título del artículo: {title}

Utiliza ÚNICAMENTE la información de los siguientes documentos para generar la sección de {section_type}:

"""
        for filename, text in content.items():
            prompt += f"[Documento: {filename}]\n{text}\n\n"
        
        prompt += f"Genera la sección de {section_type} del artículo científico. Para cada información que uses, DEBES indicar explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf]."
        
        response = self.generate_response(system_prompt, prompt, content, model_name)
        return {
            "content": response,
            "sources": list(content.keys())
        }
    
    def generate_complete_article(self, content: Dict[str, str], title: str, custom_prompt: str, model_name: str) -> Dict[str, str]:
        system_prompt = custom_prompt if custom_prompt else """
        Eres un experto en redacción académica. 
        Genera un artículo científico completo y profesional que incluya todas las secciones necesarias: 
        resumen, introducción, metodología, resultados, discusión y conclusiones.
        Para cada información que uses, DEBES indicar explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf].
        """
        
        prompt = f"""Título del artículo: {title}

Utiliza ÚNICAMENTE la información de los siguientes documentos para generar el artículo completo:

"""
        for filename, text in content.items():
            prompt += f"[Documento: {filename}]\n{text}\n\n"
        
        prompt += """
        Genera un artículo científico completo y profesional.
        IMPORTANTE:
        1. Utiliza ÚNICAMENTE la información de los documentos proporcionados
        2. Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf]
        3. No agregues información externa ni conocimiento general que no esté en los documentos
        4. Estructura el artículo en las siguientes secciones:
           - Resumen
           - Introducción
           - Metodología
           - Resultados
           - Discusión
           - Conclusiones
        """
        
        response = self.generate_response(system_prompt, prompt, content, model_name)
        return {
            "content": response,
            "sources": list(content.keys())
        }
    
    def generate_latex(self, article_content: str, title: str, authors: str) -> str:
        system_prompt = """
        Eres un experto en LaTeX y publicaciones científicas. 
        Genera código LaTeX profesional siguiendo la plantilla cup-ino.
        Incluye soporte para tablas, figuras y bibliografía.
        Mantén todas las referencias a los documentos fuente en el formato [Documento: nombre_archivo.pdf].
        """
        
        template = """\\documentclass{cup-ino}
        [... resto de la plantilla que proporcionaste ...]
        """
        
        prompt = f"""Genera código LaTeX profesional para el siguiente artículo:
        
        Título: {title}
        Autores: {authors}
        
        Contenido:
        {article_content}
        
        Usa la siguiente plantilla como base:
        {template}
        
        IMPORTANTE: Mantén todas las referencias a los documentos fuente en el formato [Documento: nombre_archivo.pdf]"""
        
        return self.generate_response(system_prompt, prompt, {}, "Llama-3-8B")
    
    def generate_bibliography(self, content: Dict[str, str], style: str, model_name: str) -> Dict[str, str]:
        system_prompt = f"""
        Eres un experto en citación académica. {self.citation_styles[style]}
        IMPORTANTE: Genera referencias ÚNICAMENTE para los documentos proporcionados.
        No agregues referencias adicionales que no estén en los documentos fuente.
        """
        
        prompt = """Extrae y genera las referencias bibliográficas ÚNICAMENTE de los siguientes documentos:

"""
        for filename, text in content.items():
            prompt += f"[Documento: {filename}]\n{text}\n\n"
        
        response = self.generate_response(system_prompt, prompt, content, model_name)
        return {
            "content": response,
            "sources": list(content.keys())
        }
    
    def answer_question(self, content: Dict[str, str], question: str, custom_prompt: str, model_name: str) -> Dict[str, str]:
        system_prompt = custom_prompt if custom_prompt else """
        Eres un asistente académico experto. 
        Tu tarea es responder preguntas basándote ÚNICAMENTE en la información proporcionada en los documentos de referencia.
        Para cada información que uses en tu respuesta, DEBES citar específicamente el documento fuente usando el formato [Documento: nombre_archivo.pdf].
        No agregues información externa ni conocimiento general que no esté en los documentos proporcionados.
        """
        
        prompt = "Documentos de referencia:\n\n"
        for filename, text in content.items():
            prompt += f"[Documento: {filename}]\n{text}\n\n"
        
        prompt += f"""
        Pregunta: {question}

        IMPORTANTE:
        1. Responde ÚNICAMENTE con información de los documentos proporcionados
        2. Para cada información que uses, indica explícitamente su fuente usando el formato [Documento: nombre_archivo.pdf]
        3. No agregues información externa ni conocimiento general que no esté en los documentos
        4. Si la información necesaria para responder la pregunta no está en los documentos, indica explícitamente que no se encuentra la información
        """
        
        response = self.generate_response(system_prompt, prompt, content, model_name)
        return {
            "answer": response,
            "sources": list(content.keys())
        }