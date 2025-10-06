# Data Dictionary

## Contracts table

| Column Name   | Data Type    | Description                                                  |
| ------------- | ------------ | ------------------------------------------------------------ |
| contract_id   | SERIAL       | Unique identifier for each contract (primary key)            |
| contract_name | VARCHAR(255) | Name or title of the uploaded contract                       |
| upload_date   | TIMESTAMP    | Date and time when the contract was uploaded                 |
| raw_text      | TEXT         | Full raw text of the contract document                       |
| processed     | BOOLEAN      | Indicates whether the contract has been parsed and processed |

## Clauses table

| Column Name     | Data Type                  | Description                                                            |
| --------------- | -------------------------- | ---------------------------------------------------------------------- |
| contract_id     | INTEGER                    | Reference to the parent contract (foreign key → contracts.contract_id) |
| section_number  | VARCHAR(10)                | Section number of the clause in the contract                           |
| header          | TEXT                       | Clause header or title                                                 |
| content         | TEXT                       | Full text content of the clause                                        |
| clause_type     | VARCHAR(50)                | Classification of clause (e.g., salary, vacation, confidentiality)     |
| created_at      | TIMESTAMP                  | Timestamp when the clause record was created                           |
| **Primary Key** | (contract_id, clause_type) | Ensures one clause per type per contract                               |

## Data points table

| Column Name     | Data Type                            | Description                                                              |
| --------------- | ------------------------------------ | ------------------------------------------------------------------------ |
| contract_id     | INTEGER                              | Reference to parent contract (foreign key → contracts.contract_id)       |
| clause_type     | VARCHAR(50)                          | Reference to clause type (foreign key → clauses.clause_type)             |
| data_key        | VARCHAR(100)                         | Name of the extracted field (e.g., salary_amount, start_date)            |
| data_value      | TEXT                                 | Extracted value for the field                                            |
| data_type       | VARCHAR(20)                          | Data type of the extracted value (e.g., string, integer, boolean, float) |
| created_at      | TIMESTAMP                            | Timestamp when the data point was created                                |
| **Primary Key** | (contract_id, clause_type, data_key) | Ensures unique key per clause and contract                               |

## Indexes

| Index Name                  | Table       | Columns     | Description                                 |
| --------------------------- | ----------- | ----------- | ------------------------------------------- |
| idx_contract_id             | clauses     | contract_id | Speeds up contract lookup by ID             |
| idx_clause_type             | clauses     | clause_type | Optimizes queries by clause type            |
| idx_data_points_contract    | data_points | contract_id | Improves joins and filtering by contract    |
| idx_data_points_clause_type | data_points | clause_type | Optimizes filtering/grouping by clause type |
| idx_data_points_key         | data_points | data_key    | Speeds up searches for specific data fields |


## Clause type and data point taxonomy

| **Clause Type**      | **Data Key**                     | **Description & Keywords Used**          

| **employee_info**    | employee_birth_date              | Mentions of “Date of Birth”, “Geboortedatum”, or similar. 
| **contract_details** | contract_type                    | Mentions of fixed-term or permanent employment (e.g., “bepaalde tijd”, “onbepaalde tijd”).
| **contract_details** | job_title                        | Phrases like “function”, “position of”, “job title”. 
| **contract_details** | start_date                       | Start of employment (e.g., “starts on”, “in dienst”, “commencing”).  
| **contract_details** | contract_duration                | Duration of employment (“duur van”, “for a period of”).            
| **contract_details** | end_date                         | End date (“until”, “tot”, “expires on”).                                                         
| **contract_details** | cao_applicable                   | Mentions of a collective labor agreement (“cao”, “collective agreement”).                                 
| **contract_details** | cao_name                         | Name of the collective labor agreement (CAO) mentioned.                                                      
| **probation**        | probation_period                 | Mentions of a probation or trial period (“proeftijd”, “trial period”, “no probation”).                 
| **probation**        | probation_months                 | Duration of the probation period, usually in months.                                                  
| **working_hours**    | hours_per_week                   | Total number of hours per week (“hours per week”, “uren per week”).                                  
| **working_hours**    | employment_type                  | Mentions of full-time or part-time (“fulltime”, “parttime”, “voltijd”, “deeltijd”).                        
| **working_hours**    | work_days                        | Typical working days (“Monday to Friday”, “maandag tot vrijdag”).                                    
| **working_hours**    | work_hours                       | Working hours or schedule (“from 9:00 to 17:00”, “werktijden”).                                     
| **working_hours**    | work_location                    | Location of work (“at [city]”, “te [plaats]”, “work location”).                                       
| **working_hours**    | remote_work_possible             | Mentions of remote or hybrid work (“thuiswerken”, “work from home”, “hybrid”).                     
| **salary**           | salary_amount                    | Salary amount, usually preceded by “€” or “salary”.                                                   
| **salary**           | salary_period                    | Pay frequency (“per month”, “per year”, “per week”, “per hour”).                                        
| **vacation**         | vacation_days                    | Number of vacation days (“vacation days”, “vakantiedagen”).                                            
| **vacation**         | vacation_hours                   | Number of vacation hours (“vakantie-uren”, “vacation hours”).                                         
| **pension**          | pension_scheme                   | Mentions of pension scheme participation (“geen pensioen”, “mandatory pension”, “verplicht pensioen”).       
| **pension**          | pension_fund                     | Name of the pension fund (“Pensioenfonds [name]”).                                                    
| **termination**      | early_termination_allowed        | Mentions of early termination rights (“may terminate”, “can opzeggen”).                                
| **termination**      | notice_period                    | Mentions of a notice period (“opzegtermijn”, “notice period of X weeks/months”).                      
| **termination**      | notice_period_weeks              | Notice period duration in weeks.                                                                          
| **termination**      | notice_period_months             | Notice period duration in months.                                                                    
| **termination**      | statutory_notice                 | Reference to legal or statutory notice periods.                                                     
| **termination**      | notice_timing                    | Mentions of timing (“end of the month”, “tegen einde van de maand”).                                  
| **confidentiality**  | confidentiality_required         | Obligation of confidentiality (“verplicht tot geheimhouding”, “confidentiality obligation”).          
| **confidentiality**  | confidentiality_scope_company    | Confidentiality covers company information (“company”, “business”).                                  
| **confidentiality**  | confidentiality_scope_operations | Confidentiality covers operations (“operations”, “bedrijfsvoering”).                                 
| **confidentiality**  | confidentiality_scope_clients    | Confidentiality covers clients/customers (“clients”, “klanten”, “customers”).                         
| **confidentiality**  | confidentiality_post_employment  | Confidentiality continues after termination (“post-employment”, “na beëindiging”).                     
| **other**            | travel_allowance                 | Mentions of travel allowance (“reiskostenvergoeding”, “travel allowance”).                            
| **other**            | travel_allowance_available       | Indicates presence of travel allowance.                                                             
| **other**            | expense_allowance                | Mentions of reimbursement of expenses (“onkostenvergoeding”, “expense allowance”).                          
| **other**            | laptop_provided                  | Mentions of a company laptop or notebook provided.                                                          
| **other**            | phone_provided                   | Mentions of a mobile phone provided.                                                                  
| **other**            | company_equipment_provided       | Mentions of other equipment provided (“bedrijfsmiddelen”, “tools”, “equipment”).                     
| **other**            | company_car                      | Mentions of a company or lease car (“leaseauto”, “company car”).                                     
| **other**            | non_compete_clause               | Mentions of a non-compete clause (“concurrentiebeding”, “non-compete”).                                 
| **other**            | relation_clause                  | Mentions of a client or relation clause (“relatiebeding”, “non-solicitation”).                       
| **other**            | training_available               | Mentions of training, courses, or education (“opleidingen”, “training”).                                  
| **other**            | sick_leave_procedure             | Mentions of sick leave reporting (“ziekmelding”, “sick leave procedure”).                                 
| **other**            | sick_leave_controls              | Mentions of sickness control procedures (“controlevoorschriften”).                                  
| **other**            | collective_insurance             | Mentions of collective or group insurance.                                                            
| **other**            | health_insurance_contribution    | Mentions of health insurance or employer contribution (“ziektekostenverzekering”).                        
