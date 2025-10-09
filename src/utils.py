# src/utils.py
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from glob import glob

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_tool_params(params: str) -> Dict[str, Any]:
    """
    Parseia string de parâmetros no formato 'key=value, key2=value2'.
    
    Args:
        params: String com parâmetros separados por vírgula
        
    Returns:
        Dicionário com os parâmetros parseados
        
    Examples:
        >>> parse_tool_params("column=Amount, bins=50")
        {'column': 'Amount', 'bins': '50'}
    """
    result = {}
    if not params or not params.strip():
        return result
    
    for part in params.split(","):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            result[key.strip()] = value.strip()
    
    return result


def get_param(params_dict: Dict[str, Any], key: str, default: Any = None, param_type: type = str) -> Any:
    """
    Obtém um parâmetro do dicionário com type casting.
    
    Args:
        params_dict: Dicionário de parâmetros
        key: Chave do parâmetro
        default: Valor padrão se não encontrado
        param_type: Tipo para conversão
        
    Returns:
        Valor convertido ou default
    """
    value = params_dict.get(key, default)
    if value is None or value == default:
        return default
    
    try:
        if param_type == int:
            return int(value)
        elif param_type == float:
            return float(value)
        elif param_type == bool:
            return str(value).lower() in ('true', '1', 'yes', 'sim')
        else:
            return str(value)
    except (ValueError, TypeError):
        logger.warning(f"Failed to convert {key}={value} to {param_type}, using default {default}")
        return default


def cleanup_old_plots(plot_dir: str = "plots", max_files: int = 20, max_age_hours: int = 24):
    """
    Remove gráficos antigos para economizar espaço.
    
    Args:
        plot_dir: Diretório dos gráficos
        max_files: Número máximo de arquivos a manter
        max_age_hours: Idade máxima em horas para manter arquivos
    """
    try:
        plots = glob(os.path.join(plot_dir, "*.png"))
        if not plots:
            return
        
        # Ordenar por tempo de modificação (mais recente primeiro)
        plots.sort(key=os.path.getmtime, reverse=True)
        
        current_time = datetime.now().timestamp()
        
        for i, plot in enumerate(plots):
            # Remover se exceder max_files ou for muito antigo
            file_age_hours = (current_time - os.path.getmtime(plot)) / 3600
            
            if i >= max_files or file_age_hours > max_age_hours:
                try:
                    os.remove(plot)
                    logger.info(f"Removed old plot: {plot}")
                except Exception as e:
                    logger.error(f"Failed to remove plot {plot}: {e}")
    
    except Exception as e:
        logger.error(f"Error cleaning up plots: {e}")


def validate_column_exists(df, column: str, columns_list: list = None) -> tuple[bool, str]:
    """
    Valida se uma coluna existe no DataFrame.
    
    Args:
        df: DataFrame do pandas
        column: Nome da coluna
        columns_list: Lista de colunas disponíveis (opcional)
        
    Returns:
        Tupla (existe, mensagem_erro)
    """
    if df is None:
        return False, "No dataframe loaded"
    
    if column not in df.columns:
        available = columns_list if columns_list else df.columns.tolist()[:5]
        return False, f"Column '{column}' not found. Available: {', '.join(available)}"
    
    return True, ""


def safe_json_convert(obj: Any) -> Any:
    """
    Converte objetos numpy/pandas para tipos Python nativos para JSON.
    
    Args:
        obj: Objeto a ser convertido
        
    Returns:
        Objeto convertido para tipo nativo Python
    """
    import numpy as np
    import pandas as pd
    
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_list()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    else:
        return obj
