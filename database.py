import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional


class Database:
    def __init__(self, db_path: str = "data/analysis.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                target_role TEXT,
                seniority_goal TEXT,
                filename TEXT,
                scores_json TEXT NOT NULL,
                ats_verdict TEXT,
                overall_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, session_id: str, target_role: str, seniority_goal: Optional[str],
                     filename: str, analysis_result: Dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scores_json = json.dumps(analysis_result)
        ats_verdict = analysis_result.get('ats_readiness', {}).get('verdict', 'Unknown')
        overall_score = analysis_result.get('overall_score', 0)
        
        cursor.execute('''
            INSERT INTO analyses (session_id, target_role, seniority_goal, filename, 
                                scores_json, ats_verdict, overall_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, target_role, seniority_goal, filename, scores_json, 
              ats_verdict, overall_score))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def get_history(self, session_id: str, limit: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, target_role, filename, overall_score, ats_verdict, created_at
            FROM analyses
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'target_role': row[1],
                'filename': row[2],
                'overall_score': row[3],
                'ats_verdict': row[4],
                'created_at': row[5]
            })
        
        return history
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT scores_json, target_role, filename, created_at, seniority_goal
            FROM analyses
            WHERE id = ?
        ''', (analysis_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            analysis = json.loads(row[0])
            analysis['id'] = analysis_id
            analysis['filename'] = row[2]
            analysis['created_at'] = row[3]
            analysis['seniority_goal'] = row[4]  # Add seniority_goal to analysis
            return analysis
        
        return None
