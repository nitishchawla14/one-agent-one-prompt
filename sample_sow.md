# Sample Statement of Work (SoW) for Demo

## Project Overview
**Project Name:** Sales Analytics Dashboard for Adventure Works  
**Client:** Adventure Works Corporation  
**Duration:** 8 weeks  
**Start Date:** February 1, 2025  

## Business Objectives
Adventure Works requires a comprehensive sales analytics solution to improve decision-making and revenue optimization. The solution should provide real-time insights into sales performance, customer behavior, and product trends.

## Deliverables

### 1. Sales Performance Dashboard
- **Requirement:** Executive-level dashboard showing total sales across all channels
- **Business Need:** Management needs to track overall revenue performance
- **Success Criteria:** Real-time visibility into Internet and Reseller sales combined
- **Users:** Sales Managers, Executive Leadership

### 2. Growth Analysis Reports
- **Requirement:** Year-over-year and month-over-month growth analysis
- **Business Need:** Track business progress against historical performance
- **Success Criteria:** Automated calculation of growth percentages with trend visualization
- **Users:** Executive Leadership, Finance Team

### 3. Product Performance Analytics
- **Requirement:** Identify top-performing products by sales and category
- **Business Need:** Focus marketing efforts on high-performing items
- **Success Criteria:** Ranking system for products with drill-down capabilities
- **Users:** Product Managers, Marketing Team

### 4. Customer Segmentation Analysis
- **Requirement:** Customer analysis by geography and purchasing behavior
- **Business Need:** Targeted marketing and customer retention strategies
- **Success Criteria:** Interactive customer segmentation with demographic insights
- **Users:** Marketing Team, Customer Success

### 5. Territory Sales Analysis
- **Requirement:** Regional sales performance comparison
- **Business Need:** Optimize sales territory management and resource allocation
- **Success Criteria:** Geographic visualization with performance metrics
- **Users:** Regional Sales Managers, Territory Planners

## Data Sources
- **Primary Source:** Adventure Works Data Warehouse (Azure SQL Database)
- **Server:** adventureworks.database.windows.net
- **Database:** AdventureWorksDW
- **Tables Required:** 
  - Sales fact tables (Internet, Reseller)
  - Customer dimensions
  - Product dimensions
  - Geography dimensions
  - Date/Calendar dimension

## Technical Requirements
- **Platform:** Microsoft Fabric
- **Storage Mode:** Direct Lake for large tables, Import for dimensions
- **Refresh Frequency:** Daily for historical data, Real-time for current day
- **Mobile Support:** Responsive design for tablets and phones
- **Security:** Row-level security by sales territory
- **Performance:** Sub-3 second query response times

## Success Metrics
- **Adoption:** 90% usage by target user groups within 30 days
- **Performance:** 95% of queries complete within 3 seconds
- **Accuracy:** 100% data accuracy validated against source systems
- **Availability:** 99.9% uptime during business hours

## Timeline
- **Week 1-2:** Data modeling and semantic model development
- **Week 3-4:** Report development and initial testing
- **Week 5-6:** User acceptance testing and feedback integration
- **Week 7-8:** Deployment and user training

## Assumptions
- Fabric workspace and capacity are provisioned and available
- Source data quality is maintained at acceptable levels
- Users have appropriate Fabric licenses and access permissions
- Network connectivity to Azure SQL Database is stable and secure
