"""
Data management for the bot 
Loads job listenings from parser or cache
"""

from database.parser_ausbildung import parse_ausbildung_de
from typing import Dict,List

#Cache for saving results
_job_cache = {}