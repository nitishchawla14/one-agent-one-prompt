# Requirements Document

## Business Requirements Table

| Requirement ID | Description | User Story | Expected Behavior |
|----------------|-------------|------------|-------------------|
| PROJECT-001 | Executive-level dashboard showing total sales across all channels | As a Sales Manager, I want to track overall revenue performance so that I can make informed decisions. | Develop a dashboard in Microsoft Fabric with real-time visibility into Internet and Reseller sales combined. Use Direct Lake mode for large tables and Import mode for dimensions. |
| PROJECT-002 | Year-over-year and month-over-month growth analysis | As an Executive Leader, I want to track business progress against historical performance so that I can assess growth trends. | Create automated calculations for growth percentages with trend visualization using DAX measures and calculation groups. |
| PROJECT-003 | Identify top-performing products by sales and category | As a Product Manager, I want to focus marketing efforts on high-performing items so that I can optimize campaigns. | Implement a ranking system for products with drill-down capabilities in the dashboard. Use star schema design for data modeling. |
| PROJECT-004 | Customer analysis by geography and purchasing behavior | As a Marketing Team member, I want targeted marketing and customer retention strategies so that I can improve engagement. | Develop interactive customer segmentation with demographic insights using Fabric's enhanced date tables and Direct Lake mode. |
| PROJECT-005 | Regional sales performance comparison | As a Regional Sales Manager, I want to optimize sales territory management so that I can allocate resources effectively. | Create geographic visualizations with performance metrics using Fabric's mapping capabilities and row-level security. |

## Data Source Information

- **Primary Source:** Adventure Works Data Warehouse (Azure SQL Database)
- **Server:** adventureworks.database.windows.net
- **Database:** AdventureWorksDW
- **Tables Required:**
  - Sales fact tables (Internet, Reseller)
  - Customer dimensions
  - Product dimensions
  - Geography dimensions
  - Date/Calendar dimension

## Development Rules

### Workspace Management
- Work within designated Fabric workspaces.
- Use Premium Per User (PPU) or Fabric capacity for development.
- Implement proper workspace role-based access control (RBAC).
- Follow organizational naming conventions for workspaces.
- Utilize workspace lineage and impact analysis features.

### Data Source Integration
- Leverage OneLake as the unified data lake.
- Use Fabric Lakehouses for structured and unstructured data.
- Utilize Fabric Data Warehouse for enterprise scenarios.
- Implement Direct Lake mode for large datasets when possible.
- Use Dataflows Gen2 for data preparation and transformation.
- Integrate KQL Database and Eventstream for streaming scenarios.

### Security and Governance
- Implement Row-Level Security (RLS) at the semantic model level.
- Use Microsoft Purview integration for data governance.
- Apply sensitivity labels for data classification.
- Follow principle of least privilege for data access.
- Implement data lineage tracking across Fabric items.

## Semantic Model Naming Conventions

- Use clear, descriptive names for tables and columns (e.g., `Sales Fact`, `Customer Dimension`).
- Prefix measures with their purpose (e.g., `Total Sales`, `YoY Growth`).
- Follow camelCase or PascalCase for naming conventions.
- Use annotations in TMDL files for documentation.

## Fabric-Specific Implementation Guidelines

### Semantic Model Development
- Use Direct Lake mode for Fabric Lakehouse tables when possible.
- Implement Import mode for smaller dimension tables.
- Use DirectQuery only when real-time data is critical.
- Create shared semantic models for enterprise-wide metrics.
- Implement incremental refresh for large fact tables.
- Use calculation groups for time intelligence patterns.

### Data Modeling Best Practices
- Follow star schema design principles.
- Create dedicated date dimension tables.
- Implement surrogate keys for dimension tables.
- Use Delta Lake format for all lakehouse tables.
- Leverage Fabric's automatic table optimization.
- Implement partition elimination strategies.

### Report Development Standards
- Utilize Fabric navigation between items.
- Implement cross-workspace reporting when authorized.
- Use real-time visuals for streaming data.
- Configure mobile-optimized layouts.
- Implement accessibility standards (WCAG 2.1).

### Performance Guidelines
- Limit visuals per report page (max 15-20).
- Use visual-level filters efficiently.
- Implement cross-filtering optimization.
- Configure query reduction settings.
- Monitor query performance through Fabric metrics.

### Security Implementation
- Implement Microsoft Purview integration.
- Use sensitivity labels on datasets and reports.
- Configure data loss prevention policies.
- Set up audit logging for compliance.
- Implement conditional access policies.

### Testing and Deployment
- Validate data accuracy across Fabric items.
- Test Direct Lake performance vs Import mode.
- Verify security roles and RLS implementation.
- Test cross-workspace dependencies.
- Validate mobile experience on different devices.
- Use Fabric deployment pipelines for CI/CD.
- Implement automated testing with Fabric REST APIs.

### Monitoring and Maintenance
- Set up Fabric monitoring dashboards.
- Configure alert notifications for refresh failures.
- Monitor usage metrics and optimization opportunities.
- Implement capacity monitoring for performance.
- Conduct regular security reviews and access audits.