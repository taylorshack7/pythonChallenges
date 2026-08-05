from datetime import datetime
import sqlite3
import json
from pathlib import Path
DB_PATH = Path(__file__).parent / 'capstone.db'

class DatabaseInitializer():
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
    def create_services_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS Services (
            ID INTEGER PRIMARY KEY, 
            Name TEXT UNIQUE NOT NULL
            );
            """)
    def create_servicedependencies_table(self):
        self.conn.execute(("""
            CREATE TABLE IF NOT EXISTS ServiceDependencies (
            ID INTEGER PRIMARY KEY,
            ServiceID INTEGER NOT NULL REFERENCES Services(ID),
            DependsOnServiceID INTEGER NOT NULL REFERENCES Services(ID),
            UNIQUE (ServiceID, DependsOnServiceID)
            );
            """))
    def create_incidenttimes_table(self):
        self.conn.execute(("""
            CREATE TABLE IF NOT EXISTS IncidentTimes (
            ID INTEGER PRIMARY KEY,
            ServiceID INTEGER NOT NULL REFERENCES Services(ID),
            IncidentTime INTEGER NOT NULL
            );
            """))
    def create_serviceanalyzerruns_table(self):
        self.conn.execute(("""
            CREATE TABLE IF NOT EXISTS ServiceAnalyzerRuns (
            ID INTEGER PRIMARY KEY,
            StartServiceId INTEGER NOT NULL REFERENCES Services(ID),
            DateCreated TEXT NOT NULL
            );
            """))
    def create_serviceanalyzerresults_table(self):
        self.conn.execute(("""
            CREATE TABLE IF NOT EXISTS ServiceAnalyzerResults (
            ID INTEGER PRIMARY KEY,
            AnalysisRunId INTEGER NOT NULL REFERENCES ServiceAnalyzerRuns(ID),
            AnalysisType TEXT NOT NULL,
            Result TEXT NOT NULL,
            UNIQUE (AnalysisRunId, AnalysisType)
            );
            """))

class ServicesToSQL():
    def __init__(self, services):
        self.services = services
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
    def add_service_sql(self):
        for service_name in self.services:
            self.conn.execute("""
            INSERT OR IGNORE INTO services (name)
            VALUES (?)""", (service_name,))
        #self.conn.commit()
        #conn.close()
    def get_service_idmap(self):
        rows = self.conn.execute("""
        Select Id, name 
        FROM Services""").fetchall()
        return {name: id for id, name in rows}
    def add_servicedependency_sql(self):
        self.service_idmap = self.get_service_idmap()
        for service_name in self.services:
            for dependency_name in self.services[service_name]["depends_on"]:
                self.conn.execute("""
                INSERT OR IGNORE INTO ServiceDependencies (ServiceId, DependsOnServiceId)
                VALUES (?,?)""", (self.service_idmap[service_name],self.service_idmap[dependency_name],))
    def add_serviceincident_sql(self):
        self.conn.execute('DELETE FROM IncidentTimes')
        for service_name in self.services:
            for incident_time in self.services[service_name]["incidents"]:
                self.conn.execute("""
                INSERT OR IGNORE INTO IncidentTimes (ServiceId, IncidentTime)
                VALUES (?, ?)""", (self.service_idmap[service_name], incident_time,))

    def commit_to_DB(self):
        self.conn.commit()
    def close_DB_connection(self):
        self.conn.close()

class AnalyzerToSQL():
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
    def add_analyzerrun_sql(self, start_service_input, service_map):
        #service_map = ServicesToSQL.get_service_idmap()
        current_time = datetime.now().isoformat()
        cur = self.conn.execute("""
        INSERT INTO ServiceAnalyzerRuns (StartServiceId, DateCreated)
        VALUES (?,?)""", (service_map[start_service_input], current_time,))
        self.new_run_id = cur.lastrowid
    def add_analyzerresults_sql(self, result_dict):
        for analysis_type in result_dict:
            self.conn.execute("""
            INSERT INTO ServiceAnalyzerResults (AnalysisRunId, AnalysisType, Result) 
            VALUES (?,?,?)""", (self.new_run_id, analysis_type, json.dumps(result_dict[analysis_type])))
    def commit_to_DB(self):
        self.conn.commit()
    def close_DB_connection(self):
        self.conn.close()