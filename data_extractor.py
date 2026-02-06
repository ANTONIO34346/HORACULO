# python/app/data_extractor.py
import re

def extract_hard_data(texts):
    """
    Varre uma lista de textos em busca de factos numéricos: 
    Percentagens, Valores Monetários e Datas.
    """
    # Regex para capturar: 10%, +5.4%, -0.2pp
    pct_pattern = r'([+-]?\d+(?:\.\d+)?\s?%)'
    # Regex para capturar: $100M, €1.5bn, USD 50k
    val_pattern = r'([$€£]|USD|EUR|BRL)\s?\d+(?:\.\d+)?\s?(?:M|bn|k|milhões|bilhões)?'
    
    extracted = {
        "percentages": [],
        "monetary": [],
        "key_numbers": []
    }
    
    combined_text = " ".join(texts)
    
    # Extração
    extracted["percentages"] = list(set(re.findall(pct_pattern, combined_text)))
    extracted["monetary"] = list(set(re.findall(val_pattern, combined_text)))
    
    # Limitar para não poluir o prompt (top 10 de cada)
    extracted["percentages"] = extracted["percentages"][:10]
    extracted["monetary"] = extracted["monetary"][:10]
    
    return extracted

def format_data_for_prompt(data_dict):
    """Transforma o dicionário numa string legível para o LLM."""
    if not data_dict["percentages"] and not data_dict["monetary"]:
        return "Nenhum dado numérico concreto detectado."
    
    res = "DADOS CONCRETOS DETECTADOS:\n"
    if data_dict["percentages"]:
        res += f"- Variações/Percentagens: {', '.join(data_dict['percentages'])}\n"
    if data_dict["monetary"]:
        res += f"- Valores/Moeda: {', '.join(data_dict['monetary'])}\n"
    return res
