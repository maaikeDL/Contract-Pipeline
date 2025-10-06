import re
import psycopg2
from psycopg2.extras import execute_values
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import json


@dataclass
class Clause:
    """Represents an extracted contract clause"""
    section_number: str
    header: str
    content: str
    clause_type: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class ContractParser:
    """Parses employment contracts and extracts structured clauses"""
    
    def __init__(self):
        self.clause_patterns = {
            'employee_info': r'gegevens werknemer|employee information|werknemer gegevens',
            'contract_details': r'gegevens arbeidsovereenkomst|contract details|arbeidsovereenkomst',
            'probation': r'proeftijd|probation|trial period',
            'working_hours': r'werktijden|working hours|plaats werkzaamheden|work location',
            'salary': r'loon|salaris|vakantietoeslag|salary|wage|compensation',
            'vacation': r'vakantiedagen|vacation days|leave|verlof',
            'pension': r'pensioen|pension|retirement',
            'termination': r'opzegging|termination|notice|beëindiging',
            'confidentiality': r'geheimhouding|confidentiality|nda|non-disclosure',
            'other': r'overige|other|additional|aanvullend',
        }
    
    def parse_contract(self, contract_text: str) -> List[Clause]:
        """Parse contract text into structured clauses"""
        clauses = []
        section_pattern = r'\*\*(\d+)\.?\s+([^\*]+?)\s*\*\*'
        sections = re.split(section_pattern, contract_text)
        
        for i in range(1, len(sections), 3):
            if i + 1 < len(sections):
                section_num = sections[i].strip()
                header = sections[i + 1].strip()
                content = sections[i + 2].strip() if i + 2 < len(sections) else ""
                
                if content:
                    clause = Clause(
                        section_number=section_num,
                        header=header,
                        content=content
                    )
                    clauses.append(clause)
        
        return clauses
    
    def classify_clause(self, clause: Clause) -> str:
        """Classify clause type based on header content"""
        header_lower = clause.header.lower()
        
        for clause_type, pattern in self.clause_patterns.items():
            if re.search(pattern, header_lower, re.IGNORECASE):
                return clause_type
        
        return 'unclassified'
    
    def extract_structured_data(self, clause: Clause) -> Dict[str, Any]:
        """Extract structured data based on clause type using regex patterns"""
        data = {}
        content = clause.content
        
        if clause.clause_type == 'employee_info':
            # Extract birth date
            birth_match = re.search(r'(?:Geboortedatum|Date of birth|Birth date):\s*([^\n]+)', content, re.IGNORECASE)
            if birth_match:
                data['employee_birth_date'] = birth_match.group(1).strip()
        
        elif clause.clause_type == 'salary':
            # Extract salary amount
            salary_match = re.search(r'€\s*([\d.,]+)', content)
            if salary_match:
                data['salary_amount'] = salary_match.group(1)
            
            # Extract salary period
            if re.search(r'per\s+maand|per\s+month', content, re.IGNORECASE):
                data['salary_period'] = 'monthly'
            elif re.search(r'per\s+jaar|per\s+year', content, re.IGNORECASE):
                data['salary_period'] = 'yearly'
            elif re.search(r'per\s+week|per\s+week', content, re.IGNORECASE):
                data['salary_period'] = 'weekly'
            elif re.search(r'per\s+uur|per\s+hour', content, re.IGNORECASE):
                data['salary_period'] = 'hourly'
        
        elif clause.clause_type == 'vacation':
            # Extract vacation days
            days_match = re.search(r'(\d+)\s+vakantiedagen|(\d+)\s+vacation days', content, re.IGNORECASE)
            if days_match:
                days = days_match.group(1) or days_match.group(2)
                data['vacation_days'] = int(days)
            
            # Extract vacation hours
            hours_match = re.search(r'(\d+)\s+vakantie-uren|(\d+)\s+vacation hours', content, re.IGNORECASE)
            if hours_match:
                hours = hours_match.group(1) or hours_match.group(2)
                data['vacation_hours'] = int(hours)
        
        elif clause.clause_type == 'working_hours':
            # Extract hours per week
            hours_match = re.search(r'(\d+)\s+uur per week|(\d+)\s+hours per week', content, re.IGNORECASE)
            if hours_match:
                hours = hours_match.group(1) or hours_match.group(2)
                data['hours_per_week'] = int(hours)
            
            # Determine employment type
            if re.search(r'\bfulltime\b|\bfull-time\b|\bvoltijd\b', content, re.IGNORECASE):
                data['employment_type'] = 'fulltime'
            elif re.search(r'\bparttime\b|\bpart-time\b|\bdeeltijd\b', content, re.IGNORECASE):
                data['employment_type'] = 'parttime'
            
            # Extract work days (e.g., dinsdag tot vrijdag, woensdag t/m vrijdag, etc.)
            weekday = (
                r"maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|"
                r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
            )

            range_pattern = (
                rf"\b({weekday})\b\s*(?:tot(?:\s+en\s+met)?|t\/m|to|–|-|—)\s*\b({weekday})\b"
            )

            days_match = re.search(range_pattern, content, re.IGNORECASE)
            if days_match:
                start_day = days_match.group(1).capitalize()
                end_day = days_match.group(2).capitalize()
                if start_day.lower() != end_day.lower():
                    data['work_days'] = f"{start_day} to {end_day}"
                else:
                    data['work_days'] = start_day

            # Extract work hours
            time_match = re.search(r'(\d{1,2}:\d{2})\s*(?:tot|to)\s*(\d{1,2}:\d{2})', content)
            if time_match:
                start_time = time_match.group(1)
                end_time = time_match.group(2)
                data['work_hours'] = f"{start_time} - {end_time}"
            
            # Extract work location - looks for "te" or "in" followed by capitalized city name
            location_match = re.search(r'(?:\bte\b|\bin\b)\s+([A-Z][a-zA-Zé-]+(?:\s+[A-Z][a-zA-Zé-]+)?)', content)
            if location_match:
                data['work_location'] = location_match.group(1).strip()
            
            # Check for remote work
            if re.search(r'thuiswerken|remote|work from home|hybrid', content, re.IGNORECASE):
                data['remote_work_possible'] = True
        
        elif clause.clause_type == 'probation':
            # Check if there's a probation period (Y/N)
            if re.search(r'geen proeftijd|no probation|no trial', content, re.IGNORECASE):
                data['probation_period'] = 'No'
                data['probation_months'] = 0
            else:
                # Look for probation duration
                period_match = re.search(r'(\d+)\s+(maand|maanden|month|months)', content, re.IGNORECASE)
                if period_match:
                    data['probation_period'] = 'Yes'
                    data['probation_months'] = int(period_match.group(1))
                else:
                    data['probation_period'] = 'Unknown'
                    data['probation_months'] = None
            
        elif clause.clause_type == 'contract_details':
            # Determine contract type
            if re.search(r'bepaalde tijd|fixed term|temporary', content, re.IGNORECASE):
                data['contract_type'] = 'fixed_term'
            elif re.search(r'onbepaalde tijd|permanent|indefinite', content, re.IGNORECASE):
                data['contract_type'] = 'permanent'
            
            # Extract job title/function
            function_match = re.search(r'functie van\s+([^\n\.]+)|position of\s+([^\n\.]+)', content, re.IGNORECASE)
            if function_match:
                function = function_match.group(1) or function_match.group(2)
                data['job_title'] = function.strip()
            
            # Extract start date
            date_patterns = [
                r'(\d{1,2}\s+\w+\s+\d{4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            ]
            for pattern in date_patterns:
                start_match = re.search(r'(?:treedt.*?op|in dienst|start|from).+?' + pattern, content, re.IGNORECASE)
                if start_match:
                    data['start_date'] = start_match.group(1)
                    break
            
            # Extract contract duration
            duration_match = re.search(r'duur van\s+([^\n]+?)\s+(?:en|\.)', content, re.IGNORECASE)
            if duration_match:
                data['contract_duration'] = duration_match.group(1).strip()
            
            # Extract end date for fixed term
            if data.get('contract_type') == 'fixed_term':
                for pattern in date_patterns:
                    end_match = re.search(r'(?:tot|until|to)\s+' + pattern, content, re.IGNORECASE)
                    if end_match:
                        data['end_date'] = end_match.group(1)
                        break
            
            # CAO (collective labor agreement) status
            if re.search(r'geen cao|geen collectieve|no cao|no collective|niet van toepassing', content, re.IGNORECASE):
                data['cao_applicable'] = False
            elif re.search(r'(?:cao|collectieve arbeidsovereenkomst).*(?:is|wordt)\s+van toepassing|collective.*agreement.*(?:is\s+)?applicable', content, re.IGNORECASE):
                data['cao_applicable'] = True
                # Extract CAO name
                cao_match = re.search(r'cao\s+([^\n\.]+?)(?:\s+(?:is|wordt)\s+van toepassing|\.|$)', content, re.IGNORECASE)
                if cao_match:
                    data['cao_name'] = cao_match.group(1).strip()
        
        elif clause.clause_type == 'pension':
            # check if there is a pension (true/false)
            if re.search(r'geen.*pensioen|no.*pension', content, re.IGNORECASE):
                data['pension_scheme'] = 'None'  # no pension
            else:
                # pension present
                # check if pension is mandatory
                if re.search(r'verplicht.*pensioen|mandatory pension|required', content, re.IGNORECASE):
                    data['pension_scheme'] = 'mandatory'
                else:
                    data['pension_scheme'] = 'voluntary'  # assume voluntary if not mandatory

                # extract only the pension fund name: look for capitalized words with optional spaces just before "Pensioenfonds"
                fund_match = re.search(r'([A-Z][a-zA-Z]*?(?:\s+[A-Z][a-zA-Z]*?)*?)\s+Pensioenfonds', content)
                if fund_match:
                    data['pension_fund'] = fund_match.group(1).strip()
        
        elif clause.clause_type == 'termination':
            # Check if termination is not allowed
            if re.search(r'kunnen.*niet.*opzeggen|cannot.*terminate|not.*terminable', content, re.IGNORECASE):
                data['early_termination_allowed'] = False
            
            # Check if termination is allowed
            elif re.search(r'kunnen.*opzeggen|can.*terminate|may.*terminate', content, re.IGNORECASE):
                data['early_termination_allowed'] = True
                
                # Extract notice period
                notice_match = re.search(r'opzegtermijn.*?(\d+)\s+(maand|maanden|month|months|week|weken|weeks)', content, re.IGNORECASE)
                if notice_match:
                    duration = int(notice_match.group(1))
                    unit = notice_match.group(2).lower()
                    if 'week' in unit:
                        data['notice_period'] = f"{duration} weeks"
                        data['notice_period_weeks'] = duration
                    else:
                        data['notice_period'] = f"{duration} months"
                        data['notice_period_months'] = duration
                
                # Check for statutory notice period
                if re.search(r'wettelijke.*opzegtermijn|statutory.*notice|legal.*notice', content, re.IGNORECASE):
                    data['statutory_notice'] = True
                
                # Extract notice timing (end of month, etc.)
                if re.search(r'tegen.*einde.*maand|end of.*month', content, re.IGNORECASE):
                    data['notice_timing'] = 'end_of_month'
        
        elif clause.clause_type == 'confidentiality':
            # Check for confidentiality obligation
            if re.search(r'verplicht tot geheimhouding|confidentiality obligation|required.*confidential', content, re.IGNORECASE):
                data['confidentiality_required'] = True
            
            # Check what is covered
            if re.search(r'bedrijf|company|business', content, re.IGNORECASE):
                data['confidentiality_scope_company'] = True
            if re.search(r'bedrijfsvoering|operations', content, re.IGNORECASE):
                data['confidentiality_scope_operations'] = True
            if re.search(r'klanten|clients|customers', content, re.IGNORECASE):
                data['confidentiality_scope_clients'] = True
            
            # Check if continues after employment
            if re.search(r'na beëindiging|after.*termination|post-employment', content, re.IGNORECASE):
                data['confidentiality_post_employment'] = True
        
        elif clause.clause_type == 'other':
            # Travel allowance
            travel_match = re.search(r'reiskostenvergoeding.*?€\s*([\d.,]+)|travel allowance.*?€\s*([\d.,]+)', content, re.IGNORECASE)
            if travel_match:
                amount = travel_match.group(1) or travel_match.group(2)
                data['travel_allowance'] = f"€{amount}"
            elif re.search(r'reiskostenvergoeding|travel allowance', content, re.IGNORECASE):
                data['travel_allowance_available'] = True
            
            # Expense allowance
            if re.search(r'onkostenvergoeding|expense allowance|expenses', content, re.IGNORECASE):
                data['expense_allowance'] = True
            
            # Equipment provision
            if re.search(r'laptop|notebook', content, re.IGNORECASE):
                data['laptop_provided'] = True
            if re.search(r'mobiele telefoon|mobile phone|smartphone', content, re.IGNORECASE):
                data['phone_provided'] = True
            if re.search(r'bedrijfsmiddelen|company equipment|tools', content, re.IGNORECASE):
                data['company_equipment_provided'] = True
            
            # Company car
            if re.search(r'leaseauto|company car|lease car', content, re.IGNORECASE):
                data['company_car'] = True
            
            # Non-compete clause
            if re.search(r'concurrentiebeding|non-compete|competition clause', content, re.IGNORECASE):
                data['non_compete_clause'] = True
            
            # Client/relation clause
            if re.search(r'relatiebeding|client clause|non-solicitation', content, re.IGNORECASE):
                data['relation_clause'] = True
            
            # Training/education
            if re.search(r'opleidingen|cursussen|training|education|course', content, re.IGNORECASE):
                data['training_available'] = True
            
            # Sick leave reporting
            if re.search(r'ziekmelding|sick leave|illness reporting', content, re.IGNORECASE):
                data['sick_leave_procedure'] = True
            if re.search(r'controlevoorschriften|control.*provisions|monitoring', content, re.IGNORECASE):
                data['sick_leave_controls'] = True
            
            # Insurance
            if re.search(r'collectieve verzekeringen|collective insurance|group insurance', content, re.IGNORECASE):
                data['collective_insurance'] = True
            if re.search(r'ziektekostenverzekering|health insurance', content, re.IGNORECASE):
                data['health_insurance_contribution'] = True
        
        return data

class DatabaseManager:
    """Manages PostgreSQL database operations"""
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None
        self.cur = None

    def connect(self):
        self.conn = psycopg2.connect(**self.db_config)
        self.cur = self.conn.cursor()

    def disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def initialize_schema(self):
        schema_sql = """
        CREATE TABLE IF NOT EXISTS contracts (
            contract_id SERIAL PRIMARY KEY,
            contract_name VARCHAR(255),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_text TEXT,
            processed BOOLEAN DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS clauses (
            contract_id INTEGER REFERENCES contracts(contract_id) ON DELETE CASCADE,
            section_number VARCHAR(10),
            header TEXT,
            content TEXT,
            clause_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (contract_id, clause_type)
        );
        CREATE TABLE IF NOT EXISTS data_points (
            contract_id INTEGER REFERENCES contracts(contract_id) ON DELETE CASCADE,
            clause_type VARCHAR(50),
            data_key VARCHAR(100) NOT NULL,
            data_value TEXT,
            data_type VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (contract_id, clause_type, data_key),
            FOREIGN KEY (contract_id, clause_type) REFERENCES clauses(contract_id, clause_type) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_contract_id ON clauses(contract_id);
        CREATE INDEX IF NOT EXISTS idx_clause_type ON clauses(clause_type);
        CREATE INDEX IF NOT EXISTS idx_data_points_contract ON data_points(contract_id);
        CREATE INDEX IF NOT EXISTS idx_data_points_clause_type ON data_points(clause_type);
        CREATE INDEX IF NOT EXISTS idx_data_points_key ON data_points(data_key);
        """
        self.cur.execute(schema_sql)
        self.conn.commit()

    def insert_contract(self, contract_name: str, raw_text: str) -> int:
        sql = """
        INSERT INTO contracts (contract_name, raw_text) VALUES (%s, %s)
        RETURNING contract_id
        """
        self.cur.execute(sql, (contract_name, raw_text))
        contract_id = self.cur.fetchone()[0]
        self.conn.commit()
        return contract_id

    def insert_clauses(self, contract_id: int, clauses: List[Clause]):
        for clause in clauses:
            sql_clause = """
            INSERT INTO clauses (contract_id, section_number, header, content, clause_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (contract_id, clause_type) DO UPDATE SET
                section_number = EXCLUDED.section_number,
                header = EXCLUDED.header,
                content = EXCLUDED.content,
                created_at = EXCLUDED.created_at
            """
            self.cur.execute(sql_clause, (
                contract_id, clause.section_number, clause.header, clause.content, clause.clause_type))
            if clause.extracted_data:
                self.insert_data_points(contract_id, clause.clause_type, clause.extracted_data)
        self.conn.commit()

    def insert_data_points(self, contract_id: int, clause_type: str, data_dict: Dict[str, Any]):
        for key, value in data_dict.items():
            if isinstance(value, bool):
                data_type = 'boolean'
                value_str = str(value).lower()
            elif isinstance(value, int):
                data_type = 'integer'
                value_str = str(value)
            elif isinstance(value, float):
                data_type = 'float'
                value_str = str(value)
            else:
                data_type = 'string'
                value_str = str(value)
            sql = """
            INSERT INTO data_points (contract_id, clause_type, data_key, data_value, data_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (contract_id, clause_type, data_key) DO UPDATE SET
                data_value = EXCLUDED.data_value,
                data_type = EXCLUDED.data_type,
                created_at = EXCLUDED.created_at
            """
            self.cur.execute(sql, (contract_id, clause_type, key, value_str, data_type))

    def mark_contract_processed(self, contract_id: int):
        sql = "UPDATE contracts SET processed = TRUE WHERE contract_id = %s"
        self.cur.execute(sql, (contract_id,))
        self.conn.commit()

    def get_clauses_by_type(self, clause_type: str) -> List[Dict]:
        sql = """
        SELECT c.contract_id, ct.contract_name, c.section_number, c.header, c.content,
        COALESCE(
            json_object_agg(dp.data_key, dp.data_value)
            FILTER (WHERE dp.data_key IS NOT NULL), '{}'::json
        ) as extracted_data
        FROM clauses c
        JOIN contracts ct ON c.contract_id = ct.contract_id
        LEFT JOIN data_points dp
            ON c.contract_id = dp.contract_id AND c.clause_type = dp.clause_type
        WHERE c.clause_type = %s
        GROUP BY c.contract_id, ct.contract_name, c.section_number, c.header, c.content
        ORDER BY c.contract_id, c.section_number
        """
        self.cur.execute(sql, (clause_type,))
        columns = [desc[0] for desc in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur.fetchall()]

    def get_contract_summary(self, contract_id: int) -> Dict:
        sql_basic = """
        SELECT contract_name, upload_date,
        (SELECT COUNT(*) FROM clauses WHERE contract_id = %s) as total_clauses
        FROM contracts
        WHERE contract_id = %s
        """
        self.cur.execute(sql_basic, (contract_id, contract_id))
        row = self.cur.fetchone()
        if not row:
            return {}
        sql_clauses = """
        SELECT clause_type, COUNT(*) as count, json_agg(data_obj) as data
        FROM (
            SELECT c.clause_type,
            json_object_agg(dp.data_key, dp.data_value) FILTER (WHERE dp.data_key IS NOT NULL) as data_obj
            FROM clauses c
            INNER JOIN data_points dp
                ON c.contract_id = dp.contract_id AND c.clause_type = dp.clause_type
            WHERE c.contract_id = %s
            GROUP BY c.clause_type, c.section_number
        ) subquery
        WHERE data_obj IS NOT NULL
        GROUP BY clause_type
        """
        self.cur.execute(sql_clauses, (contract_id,))
        clause_rows = self.cur.fetchall()
        summary = {}
        for clause_type, count, data in clause_rows:
            summary[clause_type] = {
                'count': count,
                'data': data
            }
        return {
            'contract_name': row[0],
            'upload_date': row[1],
            'total_clauses': row[2],
            'summary': summary if summary else None
        }

    def get_all_data_points_by_key(self, data_key: str) -> List[Dict]:
        sql = """
        SELECT ct.contract_name, c.clause_type, dp.data_value, dp.data_type
        FROM data_points dp
        JOIN clauses c
            ON dp.contract_id = c.contract_id AND dp.clause_type = c.clause_type
        JOIN contracts ct
            ON c.contract_id = ct.contract_id
        WHERE dp.data_key = %s
        ORDER BY ct.contract_name
        """
        self.cur.execute(sql, (data_key,))
        columns = [desc[0] for desc in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur.fetchall()]

    def compare_data_points(self, data_key: str) -> List[Dict]:
        sql = """
        SELECT ct.contract_name, ct.contract_id, dp.data_value, dp.data_type
        FROM data_points dp
        JOIN clauses c
            ON dp.contract_id = c.contract_id AND dp.clause_type = c.clause_type
        JOIN contracts ct
            ON c.contract_id = ct.contract_id
        WHERE dp.data_key = %s
        ORDER BY CASE WHEN dp.data_type = 'integer' THEN dp.data_value::INTEGER ELSE 0 END DESC, ct.contract_name
        """
        self.cur.execute(sql, (data_key,))
        columns = [desc[0] for desc in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur.fetchall()]

class ContractPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.parser = ContractParser()
        self.db = DatabaseManager(db_config)
    
    def process_contract(self, contract_text: str, contract_name: str) -> int:
        """
        Main pipeline: parse, classify, extract, and store contract data
        Returns: contract_id
        """
        self.db.connect()
        
        try:
            print(f"\n{'='*60}")
            print(f"Processing: {contract_name}")
            print(f"{'='*60}\n")
            
            contract_id = self.db.insert_contract(contract_name, contract_text)
            print(f"✓ Contract stored with ID: {contract_id}")
            
            clauses = self.parser.parse_contract(contract_text)
            print(f"✓ Extracted {len(clauses)} clauses")
            
            print(f"\nClassifying and extracting data...")
            for clause in clauses:
                clause.clause_type = self.parser.classify_clause(clause)
                clause.extracted_data = self.parser.extract_structured_data(clause)
                
                if clause.extracted_data:
                    print(f"  [{clause.clause_type}] {clause.header}: {len(clause.extracted_data)} fields")
            
            self.db.insert_clauses(contract_id, clauses)
            self.db.mark_contract_processed(contract_id)
            print(f"\n✓ All clauses stored in database")
            
            self.print_summary(contract_id)
            
            return contract_id
            
        finally:
            self.db.disconnect()
    
    def print_summary(self, contract_id: int):
        """Print a formatted summary of the contract"""
        summary = self.db.get_contract_summary(contract_id)
        
        print(f"\n{'='*60}")
        print(f"CONTRACT SUMMARY")
        print(f"{'='*60}")
        print(f"Name: {summary.get('contract_name', 'N/A')}")
        print(f"Processed: {summary.get('upload_date', 'N/A')}")
        print(f"Total Clauses: {summary.get('total_clauses', 0)}")
        
        if summary.get('summary'):
            print(f"\nExtracted Data by Type:")
            print(f"{'-'*60}")
            for clause_type, data in summary['summary'].items():
                print(f"\n{clause_type.upper().replace('_', ' ')}:")
                for item in data['data']:
                    if item:
                        for key, value in item.items():
                            print(f"  • {key}: {value}")
        
        print(f"\n{'='*60}\n")