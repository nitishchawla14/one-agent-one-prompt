# AI Implementation Guidance
  1. **Strictly match the pbip-sample** for structure, property names, formatting, and indentation.
  2. **Use only schema-supported properties** for each TMDL/JSON object. Do NOT use unsupported keys (e.g., `description` on measures is not allowed in TMDL and will cause deployment errors).
  3. **Validate each file/section incrementally**—simulate or check for schema errors before proceeding. If a deployment error occurs, check for unsupported properties and partition block formatting.
  4. **Never use placeholders**; always use real values as specified.
  5. **Enforce a compliance checklist** before declaring the implementation complete.
  6. **Document and avoid all known TMDL/PBIP pitfalls** as listed in the spec and lessons learned.
  7. **Do not use inline comments in TMDL** files

# PBIP Knowledge Base (Authoritative Source)

Single source of truth for PBIP + TMDL implementation. All rules, pitfalls, and checklists consolidated from prior scattered documents. Machine-readable markers: RULE:, FORBID:, REQUIRED-FILE:, PITFALL:, FIX:, CHECKLIST:, STEP:, MEASURE:, PARAM:, NAMING:, FORMAT:.

---
# Technical Implementation Guidelines 🔧

## 1. PBIP Structure Requirements
- Use only PBIP Report artifacts in the main .pbip file (no semanticModel artifacts)
- Report must reference SemanticModel via relative path in definition.pbir
- All files must be in `/src` folder structure

## 2. TMDL Schema Requirements
- Relationships: Use only `fromColumn` and `toColumn` properties
- Partitions: Do NOT include `queryGroup` references
- Partitions: Do NOT include `fromTable`, `toTable`, `fromCardinality`, `toCardinality`
- LocalSettings: Use minimal schema with only `$schema` property

## 3. Schema Validation Requirements
- Sales.pbip: Use pbipProperties/1.0.0/schema.json
- definition.pbir: Use definitionProperties/1.0.0/schema.json (NOT visualContainer)
- Remove all queryGroup references from table partitions
- **CRITICAL**: Never create version.json files anywhere
- **CRITICAL**: Keep definition/ folder EMPTY in Sales.Report
## 4. Schema & JSON Compliance
RULE: Every JSON artifact must copy $schema and version values from sample
RULE: Use sample pbip-sample as canonical reference for formatting and property ordering
FORBID: Adding properties that do not exist in sample files
FORBID: Creating version.json files
FORBID: Creating report.json files

---
## 5. TMDL Core Rules
RULE: One table block per .tmdl file in tables directory
RULE: Use tabs (\t) only for indentation; no leading spaces allowed
RULE: Column names must match source schema case exactly
RULE: Measures defined only in fact table files (unless explicit design exception)
RULE: Do not add unsupported properties (e.g., description on measures if schema disallows)
RULE: No inline comments (// or /* */) in TMDL outside allowed M partition code comments
FORBID: queryGroup references
FORBID: fromTable, toTable, fromCardinality, toCardinality in relationships
FORMAT: Partition must appear as:
```
partition <Name> = m
	mode: import
	source = 
		let
			< M code >
		in
			<Result>
```
FORMAT: After 'source =' there must be a newline before 'let'
RULE: Relationship file contains only relationship blocks with fromColumn/toColumn (+ optional isActive)

---
## 6. Parameters (Expressions)
RULE: All connection server/database values must use parameters (no inline literals in partitions)
FORMAT: expression <ParameterName> = "<Value>" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
FORBID: Placeholder tokens like <YOUR_SERVER>

---
## 7. Naming Conventions
NAMING: Dimension table names singular (Product); fact tables plural (Sales)
NAMING: Preserve exact column case from source system (e.g., ProductKey, SalesAmount)
NAMING: Measures in Pascal Case with spaces where business-friendly
NAMING: Time intelligence suffixes: (LY), (YTD) if introduced
RULE: Avoid technical prefixes (dim_, fact_) in final model object names

---
## 8. Partitions
RULE: Each table must have at least one partition using import mode
RULE: Partition name should match table logical intent (Product, Sales)
RULE: M scripts limit selected columns to only those required by business requirements
PITFALL: Putting 'let' on same line as 'source =' causes UnknownKeyword parse failure
FIX: Always newline after 'source ='

---
## 9. Pitfalls & Fixes (Lessons Learned)
PITFALL: Schema URL mismatches -> load failure
FIX: Copy schema URLs from sample pbip-sample exactly
PITFALL: File reference path casing mismatch
FIX: Match relative path exactly (case-sensitive on some systems)
PITFALL: Unsupported object blocks
FIX: Remove unrecognized blocks (keep minimal set)
PITFALL: Indentation mixing spaces and tabs
FIX: Convert to tabs only
PITFALL: Partition 'source = let' inline
FIX: Split line: 'source =' newline then 'let'
PITFALL: Duplicate table blocks
FIX: Ensure exactly one table per file
PITFALL: Comments (//) inside TMDL
FIX: Remove; use validator to detect
PITFALL: Using unsupported measure properties
FIX: Restrict to formatString only (per sample) unless schema update
PITFALL: Hash (#) comment lines added to .tmdl (e.g., in model.tmdl) cause Power BI Desktop TMDL parser InvalidLineType errors
FIX: Do not include any lines beginning with '#'; validator updated to treat '# ' token as forbidden.
PITFALL: Omitting canonical database/model structural properties (compatibilityLevel, culture, defaultPowerBIDataSourceVersion, etc.) leads to divergence from sample and possible future load issues
FIX: Replicate minimal sample structure exactly: `database` block with `compatibilityLevel: 1601`; `model Model` block with culture, defaultPowerBIDataSourceVersion, discourageImplicitMeasures, sourceQueryCulture, dataAccessOptions (legacyRedirects, returnErrorValuesAsNull), and annotation PBI_ProTooling.

---
## 10. Implementation Steps
STEP: Analyze AzureSQLSchema.csv and select minimal columns
STEP: Create PBIP folder structure
STEP: Add parameters in expressions.tmdl
STEP: Define tables with columns & measures
STEP: Add relationships via simplified relationships.tmdl
STEP: Add partitions (import) with filtered column set
STEP: Run validation script scripts/validate-pbip.ps1
STEP: Open project in Power BI Desktop to confirm load

---
## 11. Compliance Checklist
CHECKLIST: Report definition folder empty
CHECKLIST: No version.json anywhere
CHECKLIST: No report.json anywhere
CHECKLIST: All required files present
CHECKLIST: All partitions follow format (source newline rule)
CHECKLIST: No forbidden tokens // or queryGroup in .tmdl
CHECKLIST: Relationship file only fromColumn/toColumn
CHECKLIST: Tab-only indentation (no leading spaces)
CHECKLIST: One table block per table file
CHECKLIST: Column names match source schema
CHECKLIST: No placeholders in parameters

---
## 12. Validation Automation Contract
RULE: Validation script must fail build (exit code 1) if any CHECKLIST item not satisfied
RULE: Partition regex: partition\s+.+?=\s+m[\r\n]+\t+mode:\s+import[\r\n]+\t+source\s*=\s*[\r\n]+\t+let
RULE: Future validator enhancements should be additive only; never remove existing checks without approval
RULE: Validator must flag any occurrence of '# ' in .tmdl files (hash comments not permitted)
RULE: Consider future enhancement: broaden hash detection to lines starting with optional leading tabs/spaces followed by '#'

---
## 13. Future Enhancements Backlog
BACKLOG: Date dimension & time intelligence measures
BACKLOG: Calculation groups for time variants
BACKLOG: Incremental refresh strategy
BACKLOG: Git pre-commit hook enforcing validator
BACKLOG: CI integration (GitHub Actions) to run validator
BACKLOG: JSON rule manifest (scripts/pbip-rules.json) for dynamic configuration

---
## 14. Deprecated / Superseded Guidance
DEPRECATED: Using comments in TMDL for object descriptions
REPLACED-BY: External documentation or README; rely on formatString and structural clarity
DEPRECATED: Multi-line DAX fenced with backticks in TMDL (not supported)
REPLACED-BY: Keep single-line or indentation-based multi-line without markdown fences

---
## 15. Quick Reference (Machine Read)
FORBID: version.json
FORBID: report.json
FORBID: queryGroup
FORBID: // (in .tmdl)
REQUIRED-FILE: see Section 2 list
FORMAT: partition block pattern enforced via regex

---
## 16. Change Log
CHANGE: 2025-09-16 Consolidated requirements-01 into kb-pbip single source
CHANGE: 2025-09-16 Added explicit machine markers (RULE:, FORBID:, etc.)
CHANGE: 2025-09-16 Added pitfalls for hash (#) comments and missing model/database canonical properties; validator updated to forbid '# '

---
## 17. Source Schema Reference
The authoritative column list and data types are stored in `/.requirements/AzureSQLSchema.csv`. Always cross-check before adding or renaming columns.

---
## 18. Usage
1. Implement or modify model
2. Run validator script
3. Resolve violations
4. Open PBIP in Desktop and confirm load
5. Commit changes only after clean validation

---

## 🚨 CRITICAL RULES: 
### COMPLETE IMPLEMENTATION GUIDE
#### Step 1: Basic rules
1. Analyse the sample files provided in `pbip-sample` folder and the schema generated.
2. All files must strictly adhere to the keys, structure, formatting and style outlined in the `pbip-sample` folder.. This is non-negotiable and essential for compliance with the project requirements. It is also required that all the files are created without missing any. It is strictly required that all the files must have schema and version matched with the sample file.
3. Keep all the headers/keys/columns/sections identical to the sample.
4. Keep the content of $schema and version values/content identical to the sample.
5. Changes values realistically but keep the same type.


#### STEP 2: Project Structure Creation
1. Create src/ folder structure exactly as shown above
2. Sales.Report/definition/ folder must exist but remain EMPTY
3. Only create definition.pbir in Sales.Report root

#### STEP 3: Schema Compliance Rules
- NO version.json files in any location
- NO report.json files in definition/ folders
- NO pages/ folders or page definitions
- Use minimal JSON schemas only

#### STEP 4: TMDL Implementation Rules
- Relationships: Only fromColumn and toColumn properties
- Partitions: Remove all queryGroup references
- Partitions: Partition block must match pbip-sample format exactly, including the syntax:
  - `partition [name] = m`
  - `mode: import`
  - `source = ...`
- Do NOT use any other partition block format. Partition name and = m are required for schema compliance.
- Use semantic model parameters for server/database

#### STEP 5: Error Prevention Checklist
- [ ] definition/ folder in Sales.Report is empty
- [ ] No version.json files created
- [ ] No complex report structures
- [ ] Relationships use simplified syntax
- [ ] All queryGroup references removed

### Implementation Compliance Checklist 🚦
- All TMDL table and column names must match the actual SQL database schema exactly (case, spelling, and schema) as listed in AzureSQLSchema.csv.
- Every TMDL table must include at least one partition using the exact format and structure as the pbip-sample, with `partition [name] = m`, `mode: import`, and a valid source. Do not use unsupported properties or queryGroup.
- All connection details (server, database) must be set to the actual values provided in the requirements. Do not use placeholders like <YOUR_SERVER> or <YOUR_DATABASE>.
- Only use properties supported by the TMDL schema for each object type. Do NOT add `description` or other unsupported properties to measures or columns.
- All file structure, schema, and formatting must match the pbip-sample exactly, including partition and annotation syntax.
- Before finalizing, validate that:
  - All table/column names match the database.
  - All partitions are present and use the correct pbip-sample partition block format.
  - No placeholders remain.
  - No unsupported properties are used (especially on measures).
  - File/folder structure matches the sample.

## 🚨 CRITICAL TROUBLESHOOTING FIXES

### Power BI Desktop Loading Issues Resolution

**Issue 1: Missing version.json files**
- Solution: DO NOT create version.json files anywhere
- Reason: Power BI Desktop cannot resolve Microsoft schema URLs

**Issue 2: Schema validation errors**
- Solution: Use only minimal, validated schema patterns
- Avoid: Custom properties, complex nested structures

**Issue 3: "Definition contains no pages" error**
- Solution: Keep Sales.Report/definition/ folder completely EMPTY
- Do NOT create: report.json, version.json, pages/ folders inside definition/

**Issue 4: Relationship syntax errors**
- Solution: Use only fromColumn/toColumn properties
- Remove: fromTable, toTable, fromCardinality, toCardinality

**Issue 5: QueryGroup partition errors**
- Solution: Remove all queryGroup references from table partitions
- Keep only: mode and source properties


**Key Success Factors**: 
1. Empty definition/ folder in .Report
2. No version.json files anywhere  
3. Minimal schema compliance
4. Simplified TMDL syntax patterns

### Schema Validation Requirements
- Sales.pbip: Use pbipProperties/1.0.0/schema.json
- definition.pbir: Use definitionProperties/1.0.0/schema.json (NOT visualContainer)
- Remove all queryGroup references from table partitions

## 🚨 CRITICAL TROUBLESHOOTING FIXES

### Power BI Desktop Loading Issues Resolution

**Issue 1: Missing version.json files**
- Solution: Remove all version.json files from both Sales.Report and Sales.SemanticModel
- Reason: Power BI Desktop expects these files but schema URLs are not accessible

**Issue 2: Complex report.json structure**
- Solution: Simplify Sales.Report structure to contain only definition.pbir
- Remove: definition/ folder, report.json, version.json from Sales.Report
- Keep: Only definition.pbir with definitionProperties schema

**Issue 3: Schema validation errors**
- Problem: Schema URLs in version.json cannot be resolved
- Solution: Avoid creating version.json files entirely
- Alternative: Use minimal schema-compliant structures

**Key Learning**: Power BI Desktop's PBIP support requires very specific file structures and minimal JSON schemas. Complex report definitions cause compatibility issues.

# Semantic Model Naming conventions 🏷️

- Use singular names for dimension tables
- Use plural names for fact tables
- All model object names should be lower case
- Don't use 'fact' or 'dim' in the table or column names. Prefer business friendly representation
- Don't use column names like 'product name' prefer 'product' instead
- Measure names should follow a consistent naming convention: 
  - [measure name] for base measure
  - [measure name (ly)] for last year value of the base measure
  - [measure name (ytd)] for ytd value for the base measure

## Critical Schema and Structure Compliance 🚨

All files must strictly adhere to the format and structure outlined in the `pbip-sample` folder located in the `.resources` directory. This is **non-negotiable** and essential for compliance with the project requirements. 

### Key Points:
- All files must be created without missing any.
- The schema and version of all files must match the sample files in `pbip-sample`.
- The `pbip-sample` folder serves as the **authoritative reference** for file structure and schema.

### Developer Action:
Ensure that this requirement is explicitly included in all development specifications and thoroughly validated during implementation.


# TMDL Pitfalls and Troubleshooting Lessons Learned (2025-09-15)

## Common Issues Encountered

- **Table and Measure Naming**
  - Table names are case-sensitive. Use the exact case everywhere (e.g., `Sales` not `sales`).
  - In DAX expressions and measure definitions, always use single quotes around table and column names (e.g., `'Sales'[SalesAmount]`).

- **Indentation**
  - TMDL requires strict tab-only indentation. Do not use spaces.
  - All top-level objects (columns, measures, partitions) must be indented with a single tab under the table.
  - Properties of columns/measures/partitions must be indented with two tabs.
  - Do not mix tabs and spaces anywhere in the file.

- **Structure**
  - Only one `table` block per file. Duplicate table definitions will cause errors.
  - All columns, measures, and partitions must be inside the single table block.

- **DAX Syntax**
  - Use single quotes for table and column names in DAX.
  - Measure names should also use single quotes if they contain spaces or special characters.

- **Partition Block**
  - Ensure the partition block is present, correctly indented, and includes all required properties and annotations.

- **General**
  - Always end the file with a newline.
  - Avoid trailing spaces or blank lines.

## Error Troubleshooting Checklist

- If you see a TMDL indentation error, check for:
  - Mixed tabs and spaces
  - Incorrect property indentation
  - Case mismatches in table/measure names
  - Duplicate table definitions

---

End of Knowledge Base