"""
Simple Requirements Generator for Power BI Projects in Microsoft Fabric

This script processes:
1. Statement of Work (SoW) documents (PDF or text)
2. Power BI Rules documents (text/markdown)

And generates structured requirements.md files using Azure OpenAI API.
"""

import os
import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from openai import AzureOpenAI
from dotenv import load_dotenv
from datetime import datetime

# Optional import for PDF processing
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Load environment variables
load_dotenv()

console = Console()

class RequirementsGenerator:
    def __init__(self):
        """Initialize the Requirements Generator"""
        self.azure_client = self._setup_azure_openai()
        if not self.azure_client:
            console.print("[red]❌ Azure OpenAI client is required. Please configure your credentials.[/red]")
            exit(1)
    
    def _setup_azure_openai(self) -> Optional[AzureOpenAI]:
        """Setup Azure OpenAI client - REQUIRED"""
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        
        if not api_key or not endpoint:
            console.print("[red]Missing Azure OpenAI credentials![/red]")
            console.print("Please set the following environment variables:")
            console.print("- AZURE_OPENAI_API_KEY")
            console.print("- AZURE_OPENAI_ENDPOINT")
            console.print("- AZURE_OPENAI_DEPLOYMENT_NAME (optional, defaults to 'gpt-4')")
            return None
        
        try:
            return AzureOpenAI(
                api_key=api_key,
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01'),
                azure_endpoint=endpoint
            )
        except Exception as e:
            console.print(f"[red]Error connecting to Azure OpenAI: {e}[/red]")
            return None
    
    def extract_pdf_content(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        if not PDF_SUPPORT:
            console.print("[red]PDF support not available. Please install PyPDF2: pip install PyPDF2[/red]")
            return ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
                return content
        except Exception as e:
            console.print(f"[red]Error reading PDF: {e}[/red]")
            return ""
    
    def load_text_file(self, file_path: str) -> str:
        """Load text content from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            console.print(f"[red]Error reading file {file_path}: {e}[/red]")
            return ""
    
    def generate_requirements(self, sow_content: str, rules_content: str) -> str:
        """Generate requirements.md using Azure OpenAI"""
        
        system_prompt = """You are an expert Microsoft Fabric Power BI developer responsible for analyzing Statement of Work (SoW) documents and generating detailed technical requirements for AI agents to execute.

Your task is to create a structured requirements.md file that contains specific, actionable tasks that can be executed by AI agents in Microsoft Fabric environment.

The output should be in markdown format and include:
1. Business Requirements table with specific requirement IDs, descriptions, user stories, and expected behaviors
2. Data source information
3. Development rules
4. Semantic model naming conventions
5. Fabric-specific implementation guidelines

Focus on creating agent-executable tasks that are clear, specific, and technically accurate."""

        user_prompt = f"""Based on the following Statement of Work and Power BI Rules, generate a comprehensive requirements.md file:

STATEMENT OF WORK:
{sow_content}

POWER BI RULES:
{rules_content}

Generate a requirements.md file that includes:

1. A business requirements table with the following columns:
   - Requirement ID (format: PROJECT-001, PROJECT-002, etc.)
   - Description (brief technical description)
   - User Story (As a [role], I want [functionality] so that [benefit])
   - Expected Behavior (specific implementation details for Fabric environment)

2. Data source information extracted from the SoW

3. Development rules that AI agents should follow

4. Semantic model naming conventions

5. Fabric-specific implementation guidelines

Make sure all requirements are:
- Specific and actionable for AI agents
- Technically accurate for Microsoft Fabric environment
- Directly derived from the business needs in the SoW
- Following the rules and conventions provided

Format the output as a complete markdown document ready to be saved as requirements.md"""

        try:
            response = self.azure_client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]Error calling Azure OpenAI: {e}[/red]")
            raise
    
    def process_documents(self, sow_path: str, rules_path: str, output_path: str = None) -> str:
        """Process SoW and Rules documents to generate requirements.md"""
        
        console.print(Panel("🚀 Power BI Requirements Generator", style="bold blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Step 1: Load SoW content
            task1 = progress.add_task("📄 Loading Statement of Work...", total=None)
            if sow_path.lower().endswith('.pdf'):
                sow_content = self.extract_pdf_content(sow_path)
            else:
                sow_content = self.load_text_file(sow_path)
            
            if not sow_content:
                console.print("[red]Failed to load SoW content[/red]")
                return ""
            progress.remove_task(task1)
            
            # Step 2: Load Rules content
            task2 = progress.add_task("📋 Loading Power BI Rules...", total=None)
            rules_content = self.load_text_file(rules_path)
            if not rules_content:
                console.print("[red]Failed to load rules content[/red]")
                return ""
            progress.remove_task(task2)
            
            # Step 3: Generate requirements using Azure OpenAI
            task3 = progress.add_task("🤖 Generating requirements with Azure OpenAI...", total=None)
            requirements_content = self.generate_requirements(sow_content, rules_content)
            progress.remove_task(task3)
            
            # Step 4: Save to file
            task4 = progress.add_task("💾 Saving requirements.md...", total=None)
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"requirements_{timestamp}.md"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            progress.remove_task(task4)
        
        return output_path

@click.command()
@click.option('--sow', '-s', required=True, help='Path to Statement of Work file (PDF or text)')
@click.option('--rules', '-r', required=True, help='Path to Power BI Rules file (text/markdown)')
@click.option('--output', '-o', help='Output path for requirements.md file (optional)')
def generate_requirements(sow, rules, output):
    """Generate requirements.md for Power BI Projects using Azure OpenAI"""
    
    # Validate input files
    if not os.path.exists(sow):
        console.print(f"[red]SoW file not found: {sow}[/red]")
        return
    
    if not os.path.exists(rules):
        console.print(f"[red]Rules file not found: {rules}[/red]")
        return
    
    try:
        # Initialize generator
        generator = RequirementsGenerator()
        
        # Generate requirements
        output_file = generator.process_documents(sow, rules, output)
        
        if output_file:
            console.print(f"\n[green]✅ Requirements file generated successfully![/green]")
            console.print(f"📄 Output file: [cyan]{output_file}[/cyan]")
            
            # Show file size and preview
            file_size = os.path.getsize(output_file)
            console.print(f"📊 File size: {file_size} bytes")
            
            console.print("\n[bold]📋 Preview (first 500 characters):[/bold]")
            with open(output_file, 'r', encoding='utf-8') as f:
                preview = f.read(500)
                console.print(f"[dim]{preview}...[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error generating requirements: {e}[/red]")

if __name__ == '__main__':
    generate_requirements()
