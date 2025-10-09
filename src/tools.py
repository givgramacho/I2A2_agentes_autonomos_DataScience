# src/tools.py
import os
import json
import threading
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from langchain_core.tools import tool
import numpy as np
from typing import Optional
from datetime import datetime

from utils import parse_tool_params, logger, cleanup_old_plots

PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# ThreadLocal storage para DataFrame
_thread_local = threading.local()

def set_dataframe(df: pd.DataFrame) -> None:
    """Define o DataFrame para a thread/sessão atual."""
    _thread_local.df = df
    logger.info(f"DataFrame loaded: {df.shape[0]} rows, {df.shape[1]} columns")

def get_dataframe() -> Optional[pd.DataFrame]:
    """Obtém o DataFrame da thread/sessão atual."""
    return getattr(_thread_local, 'df', None)

def _save_plot(fig, prefix="plot"):
    """Salva gráfico e faz limpeza de arquivos antigos."""
    cleanup_old_plots(PLOT_DIR, max_files=30, max_age_hours=48)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    path = os.path.join(PLOT_DIR, f"{prefix}-{ts}.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Plot saved: {path}")
    return path

@tool
def schema_tool(dummy: str) -> str:
    """Return columns and types as JSON."""
    df = get_dataframe()
    if df is None:
        return json.dumps({"error": "No dataframe loaded."})
    
    try:
        schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
        logger.info(f"Schema retrieved: {len(schema)} columns")
        return json.dumps(schema, indent=2)
    except Exception as e:
        logger.error(f"Error in schema_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def dataset_info_tool(dummy: str) -> str:
    """
    Retorna informações completas do dataset: shape, tipos, memória, primeiras linhas.
    Útil para análise inicial exploratória.
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error": "No dataframe loaded."})
    
    try:
        # Informações básicas
        info = {
            "shape": {
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1])
            },
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
            
            # Estatísticas de valores ausentes
            "missing_values": {
                col: {
                    "count": int(df[col].isna().sum()),
                    "percentage": round(df[col].isna().sum() / len(df) * 100, 2)
                }
                for col in df.columns if df[col].isna().sum() > 0
            },
            
            # Tipos de colunas
            "column_types": {
                "numeric": df.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical": df.select_dtypes(include=['object', 'category']).columns.tolist(),
                "datetime": df.select_dtypes(include=['datetime64']).columns.tolist()
            },
            
            # Amostra dos dados
            "sample": df.head(5).to_dict(orient="records"),
            
            # Duplicatas
            "duplicates": int(df.duplicated().sum())
        }
        
        logger.info(f"Dataset info retrieved: {info['shape']}")
        return json.dumps(info, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error in dataset_info_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def missing_tool(dummy: str) -> str:
    """Return columns with missing values."""
    df = get_dataframe()
    if df is None:
        return json.dumps({"error": "No dataframe loaded."})
    
    try:
        missing = df.isnull().sum()
        missing = missing[missing > 0].to_dict()
        logger.info(f"Missing values: {len(missing)} columns")
        return json.dumps(missing)
    except Exception as e:
        logger.error(f"Error in missing_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def describe_tool(dummy: str) -> str:
    """Return descriptive statistics (only numeric columns)."""
    df = get_dataframe()
    if df is None:
        return json.dumps({"error": "No dataframe loaded."})
    
    try:
        desc = df.describe().to_dict()
        logger.info("Descriptive statistics retrieved")
        return json.dumps(desc)
    except Exception as e:
        logger.error(f"Error in describe_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def histogram_tool(params: str) -> str:
    """
    Cria histograma de uma coluna numérica.
    params: "column=Amount, bins=50" ou apenas "Amount"
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error": "No dataframe loaded."})
    
    try:
        # Parse parameters
        if not params or params.strip() == "":
            return json.dumps({"error": "Column parameter required"})
        
        column = None
        bins = 30
        
        if "=" in params:
            params_dict = parse_tool_params(params)
            column = params_dict.get("column")
            bins = int(params_dict.get("bins", 30))
        else:
            column = params.strip()
        
        if not column or column not in df.columns:
            return json.dumps({"error": f"Column '{column}' not found"})
        
        if not is_numeric_dtype(df[column]):
            return json.dumps({"error": f"Column '{column}' is not numeric"})
        
        data = df[column].dropna()
        
        if len(data) == 0:
            return json.dumps({"error": "No data available after removing NaN"})
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data, bins=bins, edgecolor='black', alpha=0.7)
        ax.set_xlabel(column, fontsize=12)
        ax.set_ylabel("Frequência", fontsize=12)
        ax.set_title(f"Histograma - {column}", fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        path = _save_plot(fig, prefix=f"hist-{column}")
        
        result = {
            "message": f"Histogram created for '{column}'",
            "plot_path": path,
            "bins": bins,
            "count": int(len(data)),
            "stats": {
                "mean": float(data.mean()),
                "median": float(data.median()),
                "std": float(data.std()),
                "min": float(data.min()),
                "max": float(data.max())
            }
        }
        
        logger.info(f"Histogram created: {column}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in histogram_tool: {e}")
        return json.dumps({"error": f"Failed: {str(e)}"})

# NÃO importar de tools_refactored aqui para evitar importação circular
# agent.py fará as importações necessárias de ambos os arquivos
