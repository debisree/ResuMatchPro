import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

try:
    import fitz
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import docx2txt
except ImportError:
    docx2txt = None


def extract_text_from_pdf(file_path: str) -> str:
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is not installed")
    
    try:
        doc = fitz.open(file_path)
        text_parts = []
        links = []
        
        for page in doc:
            page_text = page.get_text()
            if isinstance(page_text, str):
                text_parts.append(page_text)
            
            try:
                for link in page.get_links():
                    if 'uri' in link:
                        links.append(link['uri'])
            except:
                pass
        
        text = "".join(text_parts)
        
        if links:
            text += "\n\nExtracted Links:\n" + "\n".join(links)
        
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    try:
        if Document is not None:
            doc = Document(file_path)
            text_parts = []
            links = []
            
            for para in doc.paragraphs:
                text_parts.append(para.text)
                
                for run in para.runs:
                    if hasattr(run, 'element') and hasattr(run.element, 'xpath'):
                        try:
                            hyperlinks = run.element.xpath('.//w:hyperlink/@r:id')
                            for hl_id in hyperlinks:
                                try:
                                    rel = doc.part.rels[hl_id]
                                    if hasattr(rel, 'target_ref'):
                                        links.append(rel.target_ref)
                                except:
                                    pass
                        except:
                            pass
            
            text = "\n".join(text_parts)
            
            if links:
                text += "\n\nExtracted Links:\n" + "\n".join(set(links))
            
            return text
        elif docx2txt is not None:
            return docx2txt.process(file_path)
        else:
            raise ImportError("Neither python-docx nor docx2txt is installed")
    except Exception as e:
        raise Exception(f"Error parsing DOCX: {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading TXT file: {str(e)}")


def parse_resume(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def normalize_text(text: str) -> str:
    text = text.replace('\u2022', '*')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2014', '-')
    text = text.replace('\u2019', "'")
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    
    try:
        text = text.encode('ascii', errors='ignore').decode('ascii')
    except:
        pass
    
    return text


def extract_emails(text: str) -> List[str]:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(email_pattern, text, re.IGNORECASE)))


def extract_phones(text: str) -> List[str]:
    phone_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))
    return list(set(phones))


def extract_urls(text: str) -> Dict[str, List[str]]:
    urls = {
        'linkedin': [],
        'github': [],
        'portfolio': []
    }
    
    text_lower = text.lower()
    
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
    kaggle_pattern = r'(?:https?://)?(?:www\.)?kaggle\.com/[\w-]+'
    url_pattern = r'https?://(?:www\.)?[\w\-\.]+\.[\w]{2,}(?:/[\w\-\./?%&=]*)?'
    
    urls['linkedin'] = re.findall(linkedin_pattern, text, re.IGNORECASE)
    urls['github'] = re.findall(github_pattern, text, re.IGNORECASE)
    
    kaggle_urls = re.findall(kaggle_pattern, text, re.IGNORECASE)
    if kaggle_urls:
        urls['portfolio'].extend(kaggle_urls)
    
    if 'linkedin' in text_lower and not urls['linkedin']:
        urls['linkedin'].append('linkedin_detected')
    
    if 'github' in text_lower and not urls['github']:
        urls['github'].append('github_detected')
    
    portfolio_keywords = ['kaggle', 'portfolio', 'website', 'blog', 'medium.com', 
                         'dev.to', 'personal site', 'homepage']
    for keyword in portfolio_keywords:
        if keyword in text_lower and not urls['portfolio']:
            urls['portfolio'].append(f'{keyword}_detected')
            break
    
    all_urls = re.findall(url_pattern, text, re.IGNORECASE)
    for url in all_urls:
        if 'linkedin.com' not in url.lower() and 'github.com' not in url.lower():
            if url not in urls['portfolio']:
                urls['portfolio'].append(url)
    
    return urls


def extract_years(text: str) -> List[int]:
    year_pattern = r'\b(19\d{2}|20\d{2})\b'
    years = [int(y) for y in re.findall(year_pattern, text)]
    return sorted(set(years))


def extract_date_ranges(text: str) -> List[Tuple[Optional[int], Optional[int]]]:
    ranges = []
    
    patterns = [
        r'(\d{4})\s*[-–—]\s*(\d{4})',
        r'(\d{4})\s*[-–—]\s*(?:present|current|now)',
        r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4})',
        r'(\w+\s+\d{4})\s*[-–—]\s*(?:present|current|now)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            start = match[0]
            end = match[1] if len(match) > 1 else None
            
            start_year = None
            end_year = None
            
            if start and start.isdigit():
                start_year = int(start)
            elif start:
                year_match = re.search(r'\d{4}', start)
                if year_match:
                    start_year = int(year_match.group())
            
            if end and end.isdigit():
                end_year = int(end)
            elif end and end.lower() not in ['present', 'current', 'now']:
                year_match = re.search(r'\d{4}', end)
                if year_match:
                    end_year = int(year_match.group())
            elif end and end.lower() in ['present', 'current', 'now']:
                end_year = datetime.now().year
            
            if start_year:
                ranges.append((start_year, end_year))
    
    return ranges


def calculate_years_experience(date_ranges: List[Tuple[Optional[int], Optional[int]]]) -> float:
    if not date_ranges:
        return 0.0
    
    total_years = 0.0
    current_year = datetime.now().year
    
    for start, end in date_ranges:
        if start:
            end_year = end if end else current_year
            years = max(0, end_year - start)
            total_years += years
    
    return min(total_years, 50)


def detect_sections(text: str, section_hints: Dict[str, List[str]]) -> Dict[str, Dict]:
    lines = text.split('\n')
    sections = {}
    
    for section_name, hints in section_hints.items():
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            if not line_lower or len(line_lower) < 3:
                continue
            
            for hint in hints:
                if hint in line_lower and len(line_lower) < 50:
                    sections[section_name] = {
                        'found': True,
                        'line_number': i,
                        'heading': line.strip()
                    }
                    break
            
            if section_name in sections:
                break
    
    return sections


def count_bullets_in_section(text: str, section_line: int, next_section_line: Optional[int] = None) -> int:
    lines = text.split('\n')
    
    if next_section_line is None:
        next_section_line = len(lines)
    
    section_text = '\n'.join(lines[section_line:next_section_line])
    
    bullet_patterns = [
        r'^\s*[\*\-\•\◦\▪\▫\■\□\●\○]\s+',
        r'^\s*\d+\.\s+',
    ]
    
    bullet_count = 0
    for line in section_text.split('\n'):
        for pattern in bullet_patterns:
            if re.match(pattern, line):
                bullet_count += 1
                break
    
    return bullet_count


def extract_metrics(text: str, metric_patterns: List[str]) -> List[str]:
    metrics = []
    for pattern in metric_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        metrics.extend(matches)
    return metrics


def get_text_window(text: str, max_words: int = 150) -> str:
    words = text.split()
    return ' '.join(words[:max_words])
