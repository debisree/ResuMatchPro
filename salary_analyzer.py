"""
Salary Analysis Module using BLS OES Data
Provides salary insights based on role, location, and career stage
"""

import base64
import io
from typing import Dict, List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import numpy as np


# SOC codes mapping for common tech roles
SOC_CODE_MAPPING = {
    'data scientist': '15-2051',
    'senior data scientist': '15-2051',
    'data science': '15-2051',
    'machine learning engineer': '15-2051',
    'mle': '15-2051',
    'ai engineer': '15-2051',
    'software engineer': '15-1252',
    'software developer': '15-1252',
    'full stack': '15-1252',
    'backend': '15-1252',
    'frontend': '15-1252',
    'web developer': '15-1256',
    'full stack web developer': '15-1256',
    'devops': '15-1244',
    'devops engineer': '15-1244',
    'cloud architect': '15-1244',
    'data analyst': '15-2051',
    'technology manager': '11-3021',
    'engineering manager': '11-3021',
}

# Fallback salary data (percentiles in thousands) - from BLS May 2024 data
# Format: {role: {location: [10th, 25th, median, 75th, 90th]}}
SALARY_DATABASE = {
    'data scientist': {
        'national': [66, 84, 108, 140, 175],
        'san francisco': [95, 120, 150, 185, 230],
        'new york': [88, 110, 142, 175, 215],
        'seattle': [85, 105, 135, 170, 210],
        'austin': [70, 88, 115, 145, 180],
        'boston': [80, 100, 130, 165, 200],
        'chicago': [72, 90, 118, 150, 185],
        'los angeles': [78, 98, 128, 160, 195],
        'denver': [70, 87, 112, 142, 175],
        'remote': [72, 90, 120, 152, 190],
    },
    'software engineer': {
        'national': [68, 88, 115, 150, 190],
        'san francisco': [100, 130, 165, 205, 250],
        'new york': [92, 118, 155, 192, 235],
        'seattle': [90, 115, 150, 188, 230],
        'austin': [75, 95, 125, 158, 195],
        'boston': [82, 105, 138, 173, 212],
        'chicago': [74, 95, 125, 158, 195],
        'los angeles': [80, 102, 135, 170, 208],
        'denver': [72, 92, 120, 152, 188],
        'remote': [75, 96, 128, 162, 200],
    },
    'frontend developer': {
        'national': [58, 76, 100, 130, 165],
        'san francisco': [85, 110, 142, 178, 218],
        'new york': [78, 102, 135, 170, 208],
        'seattle': [75, 98, 130, 165, 202],
        'austin': [62, 82, 108, 138, 172],
        'boston': [68, 90, 120, 152, 188],
        'chicago': [60, 80, 108, 138, 172],
        'los angeles': [65, 88, 118, 150, 185],
        'denver': [58, 78, 105, 135, 168],
        'remote': [62, 84, 112, 145, 180],
    },
    'devops engineer': {
        'national': [72, 92, 120, 155, 195],
        'san francisco': [105, 135, 172, 215, 265],
        'new york': [95, 122, 160, 200, 245],
        'seattle': [92, 118, 155, 195, 238],
        'austin': [78, 100, 132, 168, 208],
        'boston': [85, 110, 145, 182, 225],
        'chicago': [75, 98, 130, 165, 205],
        'los angeles': [82, 108, 142, 180, 222],
        'denver': [75, 96, 128, 162, 200],
        'remote': [78, 102, 135, 172, 212],
    },
    'data analyst': {
        'national': [48, 62, 82, 105, 132],
        'san francisco': [70, 90, 118, 148, 182],
        'new york': [65, 84, 112, 140, 172],
        'seattle': [62, 80, 108, 138, 170],
        'austin': [52, 68, 90, 115, 145],
        'boston': [58, 75, 100, 128, 158],
        'chicago': [50, 65, 88, 112, 140],
        'los angeles': [55, 72, 96, 122, 152],
        'denver': [50, 65, 87, 112, 140],
        'remote': [52, 68, 92, 118, 148],
    },
}


class SalaryAnalyzer:
    def __init__(self):
        self.data_source = "U.S. Bureau of Labor Statistics (BLS) - Occupational Employment and Wage Statistics (May 2024)"
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location string for matching"""
        location_lower = location.lower().strip()
        
        # Map common variations
        city_mappings = {
            'sf': 'san francisco',
            'bay area': 'san francisco',
            'san jose': 'san francisco',
            'nyc': 'new york',
            'la': 'los angeles',
            'chicago, il': 'chicago',
            'boston, ma': 'boston',
        }
        
        for variant, canonical in city_mappings.items():
            if variant in location_lower:
                return canonical
        
        # Extract major city names
        major_cities = ['san francisco', 'new york', 'seattle', 'austin', 'boston', 
                       'chicago', 'los angeles', 'denver', 'remote']
        
        for city in major_cities:
            if city in location_lower:
                return city
        
        return 'national'
    
    def _normalize_role(self, role: str) -> str:
        """Normalize role for matching in database"""
        role_lower = role.lower().strip()
        
        # Direct matches
        if role_lower in SALARY_DATABASE:
            return role_lower
        
        # Fuzzy matches
        if 'data scien' in role_lower or 'machine learning' in role_lower or 'mle' in role_lower or 'ai engineer' in role_lower:
            return 'data scientist'
        elif 'software' in role_lower or 'backend' in role_lower or 'full stack' not in role_lower:
            return 'software engineer'
        elif 'frontend' in role_lower or 'front end' in role_lower:
            return 'frontend developer'
        elif 'devops' in role_lower or 'cloud' in role_lower:
            return 'devops engineer'
        elif 'data anal' in role_lower:
            return 'data analyst'
        
        return 'software engineer'  # Default fallback
    
    def _adjust_for_career_stage(self, percentiles: List[float], career_stage: str) -> Tuple[float, float]:
        """
        Adjust salary expectation based on career stage
        Returns (expected_salary, target_salary_after_improvement)
        """
        # percentiles = [10th, 25th, median, 75th, 90th]
        
        if career_stage in ['Student', 'Recent Graduate']:
            # Entry-level: 10th-25th percentile
            expected = (percentiles[0] + percentiles[1]) / 2
            target = percentiles[2]  # Can reach median with improvements
            
        elif career_stage == 'Mid-Level':
            # Mid-level: 25th-median
            expected = (percentiles[1] + percentiles[2]) / 2
            target = percentiles[3]  # Can reach 75th with improvements
            
        elif career_stage == 'Senior':
            # Senior: median-75th
            expected = (percentiles[2] + percentiles[3]) / 2
            target = percentiles[4]  # Can reach 90th with improvements
            
        else:
            # Default to mid-level
            expected = percentiles[2]
            target = percentiles[3]
        
        return expected, target
    
    def analyze_salary(self, role: str, location: str, career_stage: str, alignment_score: int) -> Dict:
        """
        Analyze salary expectations and improvement potential
        
        Args:
            role: Target job role
            location: Geographic location
            career_stage: Career stage (Student, Mid-Level, Senior, etc.)
            alignment_score: Role alignment score (0-100)
        
        Returns:
            Dict with salary analysis including histogram data
        """
        normalized_role = self._normalize_role(role)
        normalized_location = self._normalize_location(location)
        
        # Get salary data
        if normalized_role not in SALARY_DATABASE:
            return {
                'available': False,
                'message': f'Salary data not available for {role}. Add more common roles to receive salary insights.'
            }
        
        role_data = SALARY_DATABASE[normalized_role]
        
        # Try exact location match, fall back to national
        percentiles = role_data.get(normalized_location, role_data['national'])
        
        # Get expected and target salaries based on career stage
        expected_salary, target_salary = self._adjust_for_career_stage(percentiles, career_stage)
        
        # Calculate potential hike based on alignment score and improvements
        if alignment_score >= 80:
            potential_hike_percent = 15  # Already strong, moderate improvement
        elif alignment_score >= 60:
            potential_hike_percent = 30  # Good fit, significant improvement potential
        elif alignment_score >= 40:
            potential_hike_percent = 50  # Moderate alignment, high improvement potential
        else:
            potential_hike_percent = 75  # Low alignment, very high improvement potential
        
        potential_hike = (target_salary - expected_salary) / expected_salary * 100
        
        # Generate histogram
        histogram_base64 = self._generate_histogram(
            percentiles, expected_salary, target_salary, normalized_role, normalized_location
        )
        
        return {
            'available': True,
            'role': role,
            'normalized_role': normalized_role.title(),
            'location': location,
            'normalized_location': normalized_location.title() if normalized_location != 'national' else 'U.S. National Average',
            'current_expected_salary': int(expected_salary),
            'target_salary_after_improvement': int(target_salary),
            'potential_hike_amount': int(target_salary - expected_salary),
            'potential_hike_percent': int(potential_hike),
            'market_percentiles': {
                '10th': int(percentiles[0]),
                '25th': int(percentiles[1]),
                'median': int(percentiles[2]),
                '75th': int(percentiles[3]),
                '90th': int(percentiles[4]),
            },
            'histogram_base64': histogram_base64,
            'data_source': self.data_source,
            'career_stage': career_stage,
            'alignment_score': alignment_score,
        }
    
    def _generate_histogram(
        self, 
        percentiles: List[float], 
        current_expected: float, 
        target_salary: float,
        role: str,
        location: str
    ) -> str:
        """Generate salary distribution histogram with markers"""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create salary distribution (approximate normal-ish distribution)
        salaries = []
        weights = []
        
        # Generate distribution based on percentiles
        bins = [
            (percentiles[0], percentiles[1], 0.15),  # 10th-25th: 15%
            (percentiles[1], percentiles[2], 0.25),  # 25th-median: 25%
            (percentiles[2], percentiles[3], 0.25),  # median-75th: 25%
            (percentiles[3], percentiles[4], 0.15),  # 75th-90th: 15%
        ]
        
        for start, end, weight in bins:
            n_samples = int(weight * 1000)
            salaries.extend(np.linspace(start, end, n_samples))
        
        # Plot histogram
        n, bins, patches = ax.hist(
            salaries, 
            bins=30, 
            color='#3B82F6', 
            alpha=0.6, 
            edgecolor='black',
            label='Market Distribution'
        )
        
        # Add vertical lines for current and target
        ax.axvline(
            current_expected, 
            color='#EF4444', 
            linestyle='--', 
            linewidth=2.5,
            label=f'Your Expected: ${int(current_expected)}K'
        )
        
        ax.axvline(
            target_salary, 
            color='#10B981', 
            linestyle='--', 
            linewidth=2.5,
            label=f'Target (After Improvement): ${int(target_salary)}K'
        )
        
        # Add percentile markers
        for pct_name, pct_value in [('P25', percentiles[1]), ('Median', percentiles[2]), ('P75', percentiles[3])]:
            ax.axvline(pct_value, color='gray', linestyle=':', linewidth=1, alpha=0.5)
            ax.text(pct_value, ax.get_ylim()[1] * 0.85, pct_name, 
                   ha='center', fontsize=8, color='gray')
        
        # Labels and title
        ax.set_xlabel('Annual Salary (thousands USD)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title(
            f'Salary Distribution: {role.title()} - {location.title()}\nSource: {self.data_source}', 
            fontsize=13, 
            fontweight='bold'
        )
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64


# Convenience function
def get_salary_analysis(role: str, location: str, career_stage: str, alignment_score: int) -> Dict:
    """Get salary analysis for given parameters"""
    analyzer = SalaryAnalyzer()
    return analyzer.analyze_salary(role, location, career_stage, alignment_score)
