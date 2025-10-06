# Project Proposal Template

## Student Information
- Name: Maaike de Looff
- Student ID: 432732
- Email: maaikedelooff@gmail.com

## Business Context
Describe the business or domain you're working with:
- Industry: Legal
- Company/Organization: Hypothetical, in-house legal team of large organization or LegalTech vendor
- Business Problem: In-house legal teams spend significant time drafting employment contracts and ensuring they comply with company policy and legal requirements. Manual review is error-prone and time-consuming, and first drafts often require repetitive, role-specific adjustments. This project addresses the following business needs:
    * Allow in-house teams to upload drafted contracts and automatically check them against company playbooks or historical best practices, as well as regulatory requirements.
    * Automatically generate an up-to-date company playbook based on historical contract data.
    * Enable teams to draft employment contracts where only a few key data points are provided, and the system fills in the rest based on historical norms.

## Data Sources
List the data sources you plan to use:
1. **Primary Source**: Employment contracts to be reviewed, txt format
2. **Secondary Source**: Data points extracted from historic, approved employment contracts. Data points extracted from approved contracts from primary source will be added to secondary source.
3. **Supporting Data**: Regulatory framework as applicable

## Project Objectives
What will your data pipeline accomplish?
- **Primary Goal**: Build a pipeline that ingests employment contracts, extracts all clauses and key data points, checks for legal compliance and deviations from the company playbook, and produces a checklist highlighting potential gaps or risks for the user to address.
- **Secondary Goals**: 
    * Automatically generate an up-to-date company playbook summarizing historical contract norms and best practices.
    * Generate draft contracts consistent with the company playbook based on a small set of variables provided by the user (e.g., job title, contract term).
- **Success Metrics**: 
* Over 50% reduction in manual review and drafting time 
* Minimum of 90% accuracy in output
* Bonus: amount of unexpected risks flagged
 
## Technical Approach
- **Data Ingestion**: Raw employment contract text files will be parsed using regex and custom parsers to extract and classify text as individual clauses.
- **Data Processing**: Extracted data will be transformed into individual data points. Feature engineering will compute historical averages, ranges, and patterns per role/department to support ML predictions. 
- **Data Storage**: PostgreSQL database for all data points. Data points from approved contracts will be embedded in a vector database for RAG.
- **Analytics/ML**: 
    * An LLM will conduct an extra check, comparing the contract text to the extracted data points to see if there are any non-defined data points that are significant and should be extracted. These will be added to the database too.
    * Users can provide a small set of data points and an ML model will determine the most likely value for the other data points, so the full contract can be drafted.
    * An LLM will use historic data from approved contracts (embedded in vector database) to draft an up-to-date playbook for employment contracts 

## Timeline
Plan your 12-week project timeline based on your chosen components:

- **Week 1-3**: Create sample contracts and regulatory framework, set up PostgreSQL database, implement initial text parser and clause extraction and data point transformation.
- **Week 4-6**: Set up vector database, generate checklists, develop basic user interface for contract upload, displaying checklists, and viewing predicted values.
- **Week 7-9**: Integrate LLM for semantic review and gap checking, implement RAG-assisted LLM for company playbook generation.
- **Week 10-12**: Develop feature engineering pipeline, implement and test ML models to predict likely values for unspecified fields, perform end-to-end testing and validation, document results and metrics.

## Approval
**Instructor Approval**: _________________ **Date**: _________