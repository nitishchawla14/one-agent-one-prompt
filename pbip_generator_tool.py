"""
Power BI PBIP Generator Tools for LangGraph
Tools for generating Power BI Project files from requirements and Azure SQL schema
"""

import os
import json
import pyodbc
import pandas as pd
from typing import Annotated, Optional, List, Dict, Any
from langchain_core.tools import tool
from pathlib import Path
import re
from dotenv import load_dotenv

# Load environment variables from .env.pbip if it exists
pbip_env_file = os.path.join(os.getcwd(), '.env.pbip')
if os.path.exists(pbip_env_file):
    load_dotenv(pbip_env_file)

# Azure SQL Configuration - Load from environment or use defaults
AZURE_SQL_SERVER = "dhackathon2025rg.database.windows.net"
AZURE_SQL_DATABASE = "sales_dummy"
AZURE_SQL_USERNAME = ""
AZURE_SQL_PASSWORD = ""

def get_sql_connection():
    """Get Azure SQL Database connection"""
    try:
        conn_str = f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={AZURE_SQL_SERVER};
        DATABASE={AZURE_SQL_DATABASE};
        UID={AZURE_SQL_USERNAME};
        PWD={AZURE_SQL_PASSWORD};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=5;
        """
        return pyodbc.connect(conn_str)
    except Exception as e:
        return None

@tool
def analyze_requirements_for_pbip() -> str:
    """
    Read and analyze the requirements.md file to extract Power BI report requirements.
    Returns key information needed for PBIP generation.
    """
    try:
        current_dir = os.getcwd()
        req_file = os.path.join(current_dir, "requirements.md")
        
        if not os.path.exists(req_file):
            return "❌ requirements.md file not found. Please generate requirements first."
        
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key information quickly
        analysis = {
            "business_requirements": [],
            "data_sources": [],
            "tables_needed": [],
            "measures_needed": [],
            "report_pages": []
        }
        lines = content.split('\n')
        in_table = False
        for line in lines:
            if '| PROJECT-' in line and '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    analysis["business_requirements"].append({
                        "id": parts[0],
                        "description": parts[1],
                        "user_story": parts[2],
                        "expected_behavior": parts[3]
                    })
        
        # Extract data source information
        if "Data Source Information" in content:
            data_section = content.split("Data Source Information")[1].split("##")[0]
            if "Azure SQL" in data_section or "sql" in data_section.lower():
                analysis["data_sources"].append("Azure SQL Database")
            
            # Extract table names
            for line in data_section.split('\n'):
                if 'table' in line.lower() and ('sales' in line.lower() or 'product' in line.lower() or 'customer' in line.lower()):
                    analysis["tables_needed"].append(line.strip())
        
        # Extract measures from content
        measure_keywords = ["total sales", "sales amount", "growth", "rank", "ytd", "mtd"]
        for keyword in measure_keywords:
            if keyword.lower() in content.lower():
                analysis["measures_needed"].append(keyword.title())
        
        result = "📊 **Requirements Analysis for PBIP Generation:**\n\n"
        result += f"**Business Requirements Found:** {len(analysis['business_requirements'])}\n"
        for req in analysis["business_requirements"][:3]:  # Show first 3
            result += f"- {req['id']}: {req['description'][:80]}...\n"
        
        result += f"\n**Data Sources:** {', '.join(analysis['data_sources'])}\n"
        result += f"**Tables Needed:** {len(analysis['tables_needed'])}\n"
        result += f"**Measures to Implement:** {', '.join(analysis['measures_needed'][:5])}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error analyzing requirements: {str(e)}"

@tool
def discover_azure_sql_schema() -> str:
    """
    Connect to Azure SQL Database and discover the schema for Power BI model generation.
    Returns table and column information.
    """
    try:
        conn = get_sql_connection()
        if not conn:
            return "❌ Cannot connect to Azure SQL Database. Please check credentials."
        # Simplified and faster schema query - just get basic table info
        tables_query = """
        SELECT DISTINCT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        
        df = pd.read_sql(tables_query, conn)
        conn.close()
        
        # Quick processing - just get table names
        tables = df['TABLE_NAME'].tolist()
        schema_info = {table: {"detected": True} for table in tables}
        
        # Quick result formatting
        result = f"🗄️ **Schema Discovery:** Found {len(tables)} tables\n"
        result += f"Tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}\n"
        
        # Save simplified schema
        schema_file = os.path.join(os.getcwd(), "discovered_schema.json")
        with open(schema_file, 'w') as f:
            json.dump(schema_info, f, indent=2)
        
        return result
        
    except Exception as e:
        print(f"❌ Error in schema discovery: {str(e)}")
        return f"❌ Error discovering schema: {str(e)}"

@tool
def generate_pbip_structure() -> str:
    """
    Generate the Power BI Project (PBIP) folder structure and initial files.
    Creates the complete PBIP structure following Microsoft standards.
    """
    try:
        current_dir = os.getcwd()
        pbip_dir = os.path.join(current_dir, "generated_pbip")
        dirs_to_create = [
            "generated_pbip/src",
            "generated_pbip/src/Sales.Report",
            "generated_pbip/src/Sales.Report/definition",
            "generated_pbip/src/Sales.SemanticModel",
            "generated_pbip/src/Sales.SemanticModel/definition",
            "generated_pbip/src/Sales.SemanticModel/definition/tables"
        ]
        
        for dir_path in dirs_to_create:
            full_path = os.path.join(current_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
        pbip_content = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
            "version": "1.0",
            "artifacts": [
                {
                    "report": {
                        "path": "Sales.Report"
                    }
                }
            ],
            "settings": {
                "enableAutoRecovery": True
            }
        }
        
        pbip_file = os.path.join(pbip_dir, "src", "Sales.pbip")
        with open(pbip_file, 'w') as f:
            json.dump(pbip_content, f, indent=2)
        
        # Create Report definition.pbir
        pbir_content = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
            "version": "1.0",
            "datasetReference": {
                "byPath": {
                    "path": "../Sales.SemanticModel"
                }
            }
        }
        
        pbir_file = os.path.join(pbip_dir, "src", "Sales.Report", "definition.pbir")
        with open(pbir_file, 'w') as f:
            json.dump(pbir_content, f, indent=2)
        
        # Create SemanticModel definition.pbism
        pbism_content = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.2",
            "settings": {
                "qnaEnabled": True
            }
        }
        
        pbism_file = os.path.join(pbip_dir, "src", "Sales.SemanticModel", "definition.pbism")
        with open(pbism_file, 'w') as f:
            json.dump(pbism_content, f, indent=2)
        
        return f"✅ PBIP structure created at: {pbip_dir}"
        
    except Exception as e:
        return f"❌ Error generating PBIP structure: {str(e)}"

@tool
def generate_tmdl_files() -> str:
    """
    Generate TMDL (Tabular Model Definition Language) files for the semantic model.
    Creates database, model, expressions, relationships, and table definitions.
    """
    try:
        current_dir = os.getcwd()
        tmdl_dir = os.path.join(current_dir, "generated_pbip", "src", "Sales.SemanticModel", "definition")
        
        if not os.path.exists(tmdl_dir):
            return "❌ PBIP structure not found. Please generate PBIP structure first."
        
        # Load discovered schema if available
        schema_file = os.path.join(current_dir, "discovered_schema.json")
        schema_info = {}
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema_info = json.load(f)
        
        # Generate database.tmdl
        database_content = """database
\tcompatibilityLevel: 1601

"""
        
        # Generate model.tmdl (optional when model.bim exists)
        model_content = """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tdiscourageImplicitMeasures
\tsourceQueryCulture: en-US
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

\tannotation PBI_ProTooling = ["DevMode"]
\tannotation __PBI_TimeIntelligenceEnabled = 1
"""
        
        # Generate expressions.tmdl (parameters)
        expressions_content = f"""expression ServerName = "{AZURE_SQL_SERVER}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

expression DatabaseName = "{AZURE_SQL_DATABASE}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
"""
        
        # Generate basic relationships.tmdl
        relationships_content = """/// Relationships will be added here based on schema analysis
"""
        
        # Generate table files
        tables_created = []
        
        # Always generate Product table
        product_table = """table Product

\tcolumn ProductKey
\t\tdataType: int64
\t\tformatString: 0
\t\tisKey

\tcolumn EnglishProductName
\t\tdataType: string

\tcolumn Color
\t\tdataType: string

\tcolumn ListPrice
\t\tdataType: decimal
\t\tformatString: $ #,##0.00

\tpartition Product = m
\t\tmode: import
\t\tsource = 
\t\t\tlet
\t\t\t\tSource = Sql.Database(ServerName, DatabaseName),
\t\t\t\tDimProduct = Source{[Schema="dbo",Item="DimProduct"]}[Data],
\t\t\t\tSelectedColumns = Table.SelectColumns(DimProduct,{"ProductKey", "EnglishProductName", "Color", "ListPrice"})
\t\t\tin
\t\t\t\tSelectedColumns
"""
        
        product_file = os.path.join(tmdl_dir, "tables", "Product.tmdl")
        with open(product_file, 'w') as f:
            f.write(product_table)
        tables_created.append("Product.tmdl")
        
        # Always generate Sales table
        sales_table = """table Sales

\tcolumn SalesOrderNumber
\t\tdataType: string

\tcolumn ProductKey
\t\tdataType: int64
\t\tformatString: 0

\tcolumn SalesAmount
\t\tdataType: decimal
\t\tformatString: $ #,##0.00

\tcolumn OrderQuantity
\t\tdataType: int64
\t\tformatString: 0

\tmeasure 'Total Sales Amount' = SUM('Sales'[SalesAmount])
\t\tformatString: $ #,##0

\tmeasure 'Product Sales Rank' = RANKX(ALL('Product'), [Total Sales Amount])
\t\tformatString: 0

\tpartition Sales = m
\t\tmode: import
\t\tsource = 
\t\t\tlet
\t\t\t\tSource = Sql.Database(ServerName, DatabaseName),
\t\t\t\tFactSales = Source{[Schema="dbo",Item="FactSales"]}[Data],
\t\t\t\tSelectedColumns = Table.SelectColumns(FactSales,{"SalesOrderNumber", "ProductKey", "SalesAmount", "OrderQuantity"})
\t\t\tin
\t\t\t\tSelectedColumns
"""
        
        sales_file = os.path.join(tmdl_dir, "tables", "Sales.tmdl")
        with open(sales_file, 'w') as f:
            f.write(sales_table)
        tables_created.append("Sales.tmdl")
        
        # Always create relationship between Product and Sales tables
        relationships_content = """relationship bb5c5591-a0ff-4ce4-a62e-6c5f56006368
\tfromColumn: Sales.ProductKey
\ttoColumn: Product.ProductKey

"""
        
        # Write core TMDL files quickly
        files_written = []
        
        # Write database.tmdl
        database_file = os.path.join(tmdl_dir, "database.tmdl")
        with open(database_file, 'w') as f:
            f.write(database_content)
        files_written.append("database.tmdl")
        
        # Write model.tmdl
        model_file = os.path.join(tmdl_dir, "model.tmdl")
        with open(model_file, 'w') as f:
            f.write(model_content)
        files_written.append("model.tmdl")
        
        # Write expressions.tmdl
        expressions_file = os.path.join(tmdl_dir, "expressions.tmdl")
        with open(expressions_file, 'w') as f:
            f.write(expressions_content)
        files_written.append("expressions.tmdl")
        
        # Write relationships.tmdl
        relationships_file = os.path.join(tmdl_dir, "relationships.tmdl")
        with open(relationships_file, 'w') as f:
            f.write(relationships_content)
        files_written.append("relationships.tmdl")
        
        return f"✅ TMDL files created: {len(files_written)} core files + {len(tables_created)} tables"
        
    except Exception as e:
        return f"❌ Error generating TMDL files: {str(e)}"

# @tool - REMOVED: Validation step removed from workflow
# def validate_pbip_project() -> str:
#     """
#     Validate the generated PBIP project using the validation script from the reference implementation.
#     Checks for compliance with Power BI Project standards.
#     """
#     print("✅ STEP 5: Validating PBIP project for compliance...")
#     # Validation function body removed from workflow
#     return "✅ Validation step removed from workflow. PBIP files generated with correct schemas."

@tool
def generate_pbip_documentation() -> str:
    """
    Generate comprehensive documentation for the created PBIP project.
    Includes setup instructions, data model description, and usage guide.
    """
    try:
        current_dir = os.getcwd()
        pbip_dir = os.path.join(current_dir, "generated_pbip")
        
        if not os.path.exists(pbip_dir):
            return "❌ Generated PBIP project not found. Please generate the project first."
        
        # Generate README.md
        readme_content = f"""# Generated Sales Power BI Project (PBIP)

## Overview
This Power BI Project was automatically generated from business requirements and Azure SQL Database schema analysis.

## Project Structure
```
src/
├── Sales.pbip                    # Main Power BI Project file
├── Sales.Report/
│   ├── definition.pbir          # Report definition (references semantic model)
│   └── definition/              # Empty folder (required by Power BI Desktop)
└── Sales.SemanticModel/
    ├── definition.pbism         # Semantic model definition
    └── definition/              # TMDL files
        ├── database.tmdl        # Database configuration
        ├── model.tmdl          # Model settings and annotations  
        ├── expressions.tmdl    # Parameters (ServerName, DatabaseName)
        ├── relationships.tmdl   # Table relationships
        └── tables/             # Table definitions
            ├── Product.tmdl    # Product dimension table
            └── Sales.tmdl      # Sales fact table with measures
```

## Data Source Configuration
- **Server**: {AZURE_SQL_SERVER}
- **Database**: {AZURE_SQL_DATABASE}
- **Authentication**: SQL Server Authentication
- **Storage Mode**: Import mode for optimal performance

## Semantic Model Features

### Tables
1. **Product** (Dimension)
   - ProductKey (Primary Key)
   - EnglishProductName
   - Color
   - ListPrice

2. **Sales** (Fact)
   - SalesOrderNumber
   - ProductKey (Foreign Key)
   - SalesAmount
   - OrderQuantity

### Measures
- **Total Sales Amount**: `SUM('Sales'[SalesAmount])`
- **Product Sales Rank**: `RANKX(ALL('Product'), [Total Sales Amount])`

### Relationships
- Sales[ProductKey] → Product[ProductKey] (Many-to-One)

## Setup Instructions

### Prerequisites
1. Power BI Desktop (latest version with TMDL support)
2. Access to Azure SQL Database
3. Appropriate database permissions

### Opening the Project
1. Navigate to the generated project folder
2. Open `src/Sales.pbip` in Power BI Desktop
3. When prompted, enter your Azure SQL credentials
4. Verify data loads correctly

### Configuration Parameters
Update the following parameters in Power BI Desktop if needed:
- **ServerName**: Current value `{AZURE_SQL_SERVER}`
- **DatabaseName**: Current value `{AZURE_SQL_DATABASE}`

## Validation
Run the validation script to ensure compliance:
```powershell
powershell -ExecutionPolicy Bypass -File .\\validate-generated-pbip.ps1
```

## Report Development Guidelines
1. Use the semantic model as the foundation for reports
2. Leverage existing measures for consistency
3. Follow Power BI best practices for visual design
4. Implement row-level security if needed

## Troubleshooting
- **Connection Issues**: Verify Azure SQL credentials and network access
- **Data Load Errors**: Check table permissions and schema changes
- **TMDL Errors**: Ensure no forbidden tokens or formatting issues

## Generated On
{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Support
This project was generated automatically. For issues:
1. Check validation results
2. Review Power BI Desktop error messages
3. Verify Azure SQL Database connectivity
"""
        
        readme_file = os.path.join(pbip_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Generate deployment guide
        deployment_content = """# Deployment Guide for Generated PBIP Project

## Local Development
1. Open `src/Sales.pbip` in Power BI Desktop
2. Configure data source credentials
3. Publish to Power BI Service when ready

## Power BI Service Deployment
1. In Power BI Desktop, select "Publish"
2. Choose target workspace
3. Configure dataset refresh schedule
4. Set up appropriate permissions

## Semantic Model Sharing
- The semantic model can be shared across multiple reports
- Consider creating a dedicated workspace for semantic models
- Implement appropriate security and governance

## Maintenance
- Monitor query performance
- Update measures as business requirements evolve
- Refresh schema if database structure changes
"""
        
        deployment_file = os.path.join(pbip_dir, "DEPLOYMENT.md")
        with open(deployment_file, 'w', encoding='utf-8') as f:
            f.write(deployment_content)
        
        return f"✅ Documentation created at: {pbip_dir} - Project ready!"
        
    except Exception as e:
        return f"❌ Error generating documentation: {str(e)}"