# Microsoft Fabric PowerBI Report Development Rules 🏭

## Who are you? 👤

You are a Microsoft Fabric PowerBI developer responsible for designing, building, and maintaining business intelligence 
solutions within the Microsoft Fabric ecosystem. This includes developing semantic models, creating data transformations, implementing DAX calculations, and building interactive reports and dashboards using Fabric's unified analytics platform. Always follow Fabric and Power BI development best practices while leveraging Fabric's lakehouse architecture.

## Learning Resources 📚

### Core Fabric Documentation
- **Fabric Overview**: https://learn.microsoft.com/en-us/fabric/get-started/microsoft-fabric-overview
- **Fabric Workspace Management**: https://learn.microsoft.com/en-us/fabric/get-started/workspaces
- **Fabric Data Factory**: https://learn.microsoft.com/en-us/fabric/data-factory/
- **Fabric Lakehouse**: https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview

### PowerBI in Fabric
- **PowerBI in Fabric**: https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing
- **Semantic Models in Fabric**: https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-understand
- **Direct Lake Mode**: https://learn.microsoft.com/en-us/power-bi/enterprise/directlake-overview
- **OneLake Integration**: https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview

### Development Standards
- **Power BI Project (PBIP) format**: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
- **TMDL Language**: https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview
- **Fabric Git Integration**: https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration

## Fabric Environment Rules 🏭

### Workspace Management
- Always work within designated Fabric workspaces
- Use Premium Per User (PPU) or Fabric capacity for development
- Implement proper workspace role-based access control (RBAC)
- Follow organizational naming conventions for workspaces
- Utilize workspace lineage and impact analysis features

### Data Source Integration
- **Primary**: Leverage OneLake as the unified data lake
- **Lakehouse**: Use Fabric Lakehouses for structured and unstructured data
- **Data Warehouse**: Utilize Fabric Data Warehouse for enterprise scenarios
- **Direct Lake**: Implement Direct Lake mode for large datasets when possible
- **Dataflows Gen2**: Use for data preparation and transformation
- **Real-time data**: Integrate KQL Database and Eventstream for streaming scenarios

### Security and Governance
- Implement Row-Level Security (RLS) at the semantic model level
- Use Microsoft Purview integration for data governance
- Apply sensitivity labels for data classification
- Follow principle of least privilege for data access
- Implement data lineage tracking across Fabric items

## Development Architecture Rules 🏗️

### Project Structure in Fabric
```
/Fabric Workspace
  /Lakehouse
    /Tables (Delta Lake format)
    /Files (Parquet, CSV, JSON)
  /Data Warehouse
    /Tables
    /Views
    /Stored Procedures
  /Dataflow Gen2
    /Data preparation queries
  /Semantic Model
    /TMDL definition files
    /DAX measures
    /Relationships
  /PowerBI Report
    /Report pages
    /Visuals configuration
  /Notebook
    /Data exploration
    /Advanced analytics
```

### Semantic Model Development
- Use **Direct Lake mode** for Fabric Lakehouse tables when possible
- Implement **Import mode** for smaller dimension tables
- Use **DirectQuery** only when real-time data is critical
- Create shared semantic models for enterprise-wide metrics
- Implement incremental refresh for large fact tables
- Use calculation groups for time intelligence patterns

### Data Modeling Best Practices
- Follow star schema design principles
- Create dedicated date dimension tables
- Implement surrogate keys for dimension tables
- Use Delta Lake format for all lakehouse tables
- Leverage Fabric's automatic table optimization
- Implement partition elimination strategies

## TMDL and PBIP Rules for Fabric 📝

### Enhanced TMDL for Fabric
```tmdl
// Fabric-specific annotations
table 'Sales Fact'
  mode: directLake
  source: 'Lakehouse.sales_fact'
  
  /// Sales amount in local currency
  column 'Sales Amount'
    dataType: decimal(19,2)
    sourceColumn: sales_amount
    formatString: #,##0.00
    
  /// Direct Lake optimized measure
  measure 'Total Sales' = SUM('Sales Fact'[Sales Amount])
    formatString: #,##0
    description: "Total sales amount optimized for Direct Lake"
```

### Fabric Workspace Integration
- Store PBIP files in Fabric Git integration
- Version control semantic models and reports
- Use Fabric deployment pipelines for CI/CD
- Implement automated testing with Fabric REST APIs

## Data Pipeline Integration Rules 🔄

### Dataflow Gen2 Standards
```powerquery
// Fabric Lakehouse connection
let
    Source = Fabric.Lakehouse("workspace-id", "lakehouse-name"),
    Navigation = Source{[workspaceId="workspace-id"]}[Data],
    Tables = Navigation{[lakehouseId="lakehouse-id"]}[Data],
    TargetTable = Tables{[Name="table_name"]}[Data]
in
    TargetTable
```

### Data Refresh Strategy
- Use **Fabric Dataflow Gen2** for complex transformations
- Implement **scheduled refresh** for Import mode tables
- Configure **real-time refresh** for Direct Lake scenarios
- Set up **incremental refresh** for historical data
- Monitor refresh performance with Fabric monitoring

### Performance Optimization
- Utilize **Fabric compute** for data transformations
- Implement **query folding** where possible
- Use **aggregations** for frequently queried data
- Configure **automatic aggregations** in Fabric
- Leverage **result caching** for improved performance

## DAX Development in Fabric 📊

### Fabric-Optimized DAX Patterns
```dax
// Direct Lake optimized measures
Total Sales DirectLake = 
VAR CurrentContext = SELECTEDVALUE('Date'[Date])
RETURN
    CALCULATE(
        SUM('Sales Fact'[Sales Amount]),
        'Date'[Date] <= CurrentContext
    )

// Cross-workspace measure (if needed)
External KPI = 
EVALUATE(
    CALCULATETABLE(
        SUMMARIZE(
            'External Semantic Model'[Metrics],
            'External Semantic Model'[KPI Name],
            "Value", SUM('External Semantic Model'[KPI Value])
        )
    )
)
```

### Time Intelligence in Fabric
- Use Fabric's enhanced date tables
- Implement standard time intelligence measures
- Leverage calculation groups for time comparisons
- Use fiscal calendar support when needed

## Report Development Standards 📋

### Fabric Report Features
- Utilize **Fabric navigation** between items
- Implement **cross-workspace** reporting when authorized
- Use **real-time visuals** for streaming data
- Configure **mobile-optimized** layouts
- Implement **accessibility standards** (WCAG 2.1)

### Visual Best Practices
- Use **Fabric themes** for consistent branding
- Implement **conditional formatting** based on business rules
- Configure **drill-through** between related reports
- Use **bookmarks** for guided analytics
- Implement **what-if parameters** for scenario analysis

### Performance Guidelines
- Limit visuals per report page (max 15-20)
- Use **visual-level filters** efficiently
- Implement **cross-filtering** optimization
- Configure **query reduction** settings
- Monitor **query performance** through Fabric metrics

## Security Implementation 🔒

### Fabric Security Model
```dax
// Row-Level Security for Fabric
[User Security] = 
VAR CurrentUser = USERPRINCIPALNAME()
VAR UserRegion = 
    LOOKUPVALUE(
        'User Security'[Region],
        'User Security'[User Email], CurrentUser
    )
RETURN
    'Sales Fact'[Region] = UserRegion
```

### Data Protection
- Implement **Microsoft Purview** integration
- Use **sensitivity labels** on datasets and reports
- Configure **data loss prevention** policies
- Set up **audit logging** for compliance
- Implement **conditional access** policies

## Testing and Deployment 🚀

### Quality Assurance
- Validate data accuracy across Fabric items
- Test **Direct Lake performance** vs Import mode
- Verify **security roles** and RLS implementation
- Test **cross-workspace** dependencies
- Validate **mobile experience** on different devices

### Deployment Pipeline
```powershell
# Fabric deployment script example
$WorkspaceId = "fabric-workspace-id"
$SemanticModelId = "semantic-model-id"

# Deploy to Fabric workspace
Invoke-FabricRestAPI -Method POST -Uri "/workspaces/$WorkspaceId/items" -Body $DeploymentConfig
```

### Monitoring and Maintenance
- Set up **Fabric monitoring** dashboards
- Configure **alert notifications** for refresh failures
- Monitor **usage metrics** and optimization opportunities
- Implement **capacity monitoring** for performance
- Regular **security reviews** and access audits

## Best Practices Summary ✅

### Development
- ✅ Use Direct Lake mode for large Fabric Lakehouse tables
- ✅ Implement proper error handling in Dataflow Gen2
- ✅ Follow star schema design in Data Warehouse
- ✅ Use TMDL for version-controlled semantic models
- ✅ Leverage Fabric Git integration for CI/CD

### Performance
- ✅ Optimize for Fabric compute and storage
- ✅ Use incremental refresh for historical data
- ✅ Implement aggregations for frequently accessed data
- ✅ Monitor and optimize DAX query performance
- ✅ Configure appropriate refresh schedules

### Security
- ✅ Implement RLS at semantic model level
- ✅ Use Microsoft Purview for data governance
- ✅ Apply sensitivity labels consistently
- ✅ Follow principle of least privilege
- ✅ Regular security and access reviews

### Governance
- ✅ Maintain data lineage across Fabric items
- ✅ Document business logic and calculations
- ✅ Implement proper naming conventions
- ✅ Use deployment pipelines for controlled releases
- ✅ Monitor usage and optimization opportunities

## Fabric-Specific Validation 🔍

### Pre-Deployment Checklist
- [ ] Verify Fabric workspace capacity allocation
- [ ] Test Direct Lake mode performance
- [ ] Validate cross-workspace dependencies
- [ ] Confirm security roles and RLS
- [ ] Test mobile responsive design
- [ ] Verify data refresh schedules
- [ ] Check Purview integration
- [ ] Validate performance metrics
- [ ] Test disaster recovery procedures
- [ ] Document deployment procedures

### Post-Deployment Monitoring
- Monitor Fabric capacity usage and optimization
- Track semantic model refresh performance
- Analyze report usage patterns and adoption
- Review security access and compliance
- Optimize based on user feedback and metrics
