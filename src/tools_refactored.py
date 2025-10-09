# src/tools_refactored.py
# Versão refatorada das ferramentas restantes (continuação do tools.py)

import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from langchain_core.tools import tool
from datetime import datetime
from sklearn.cluster import KMeans
import seaborn as sns

from utils import parse_tool_params, logger

# Importar funções compartilhadas de tools.py
from tools import get_dataframe, _save_plot

@tool
def boxplot_tool(params: str) -> str:
    """
    Cria boxplot para visualizar distribuição e outliers.
    params: "column" ou vazio para todas as colunas numéricas
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error": "No dataframe loaded."})
    
    try:
        # Parse parameters
        columns = []
        
        if not params or params.strip() == "":
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        elif "=" not in params:
            columns = [params.strip()]
        else:
            params_dict = parse_tool_params(params)
            if "column" in params_dict:
                columns = [params_dict["column"]]
            elif "columns" in params_dict:
                columns = params_dict["columns"].split("|")
        
        if not columns:
            return json.dumps({"error": "No numeric columns found"})
        
        missing = [col for col in columns if col not in df.columns]
        if missing:
            return json.dumps({"error": f"Columns not found: {missing}"})
        
        non_numeric = [col for col in columns if not is_numeric_dtype(df[col])]
        if non_numeric:
            return json.dumps({"error": f"Non-numeric columns: {non_numeric}"})
        
        data_to_plot = []
        valid_columns = []
        
        for col in columns:
            data = df[col].dropna()
            if len(data) > 0:
                data_to_plot.append(data)
                valid_columns.append(col)
        
        if not data_to_plot:
            return json.dumps({"error": "No valid data"})
        
        # Tamanho dinâmico
        num_cols = len(valid_columns)
        fig_width = max(12, num_cols * 1.5)
        fig, ax = plt.subplots(figsize=(fig_width, 8))
        
        bp = ax.boxplot(data_to_plot, labels=valid_columns, patch_artist=True, 
                        showmeans=True, meanline=True)
        
        # Cores alternadas
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(colors[i % len(colors)])
            patch.set_alpha(0.7)
        
        for median in bp['medians']:
            median.set_color('red')
            median.set_linewidth(2)
        
        for mean in bp['means']:
            mean.set_color('blue')
            mean.set_linewidth(2)
        
        ax.set_title(f"Boxplot - {num_cols} variáveis", fontsize=14, fontweight='bold')
        ax.set_ylabel("Values", fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        path = _save_plot(fig, prefix=f"boxplot-{num_cols}vars")
        
        # Estatísticas de outliers
        outlier_stats = {}
        for col in valid_columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower) | (df[col] > upper)][col]
            outlier_stats[col] = {
                "count": int(len(outliers)),
                "percentage": round(len(outliers) / len(df) * 100, 2)
            }
        
        logger.info(f"Boxplot created for {num_cols} variables")
        return json.dumps({
            "message": f"Boxplot with {num_cols} variables",
            "plot_path": path,
            "columns": valid_columns,
            "outlier_stats": outlier_stats
        })
    except Exception as e:
        logger.error(f"Error in boxplot_tool: {e}")
        return json.dumps({"error": f"Failed: {str(e)}"})

@tool
def scatter_tool(params: str) -> str:
    """Cria gráfico de dispersão entre duas colunas numéricas. Params: x=col1, y=col2, sample=1000"""
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        x = get_param(params_dict, "x", None)
        y = get_param(params_dict, "y", None)
        sample = get_param(params_dict, "sample", None, int)
        
        if not x or not y:
            return json.dumps({"error": "x and y parameters required"})
        
        if x not in df.columns or y not in df.columns:
            return json.dumps({"error":"x or y column not found"})
        
        if not (is_numeric_dtype(df[x]) and is_numeric_dtype(df[y])):
            return json.dumps({"error":"x and y must be numeric"})
        
        data = df[[x,y]].dropna()
        if sample and sample < len(data):
            data = data.sample(sample, random_state=42)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(data[x], data[y], s=15, alpha=0.5, color='steelblue', edgecolors='navy', linewidth=0.3)
        ax.set_xlabel(x, fontsize=12)
        ax.set_ylabel(y, fontsize=12)
        ax.set_title(f"{x} vs {y}", fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)
        
        path = _save_plot(fig, prefix=f"scatter-{x}-{y}")
        logger.info(f"Scatter plot created: {x} vs {y}, n={len(data)}")
        return json.dumps({"message":"scatter created","plot_path":path, "n": len(data)})
    except Exception as e:
        logger.error(f"Error in scatter_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def correlation_tool(dummy: str) -> str:
    """Calcula matriz de correlação entre variáveis numéricas e gera mapa de calor."""
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        numeric = df.select_dtypes(include=[np.number])
        if numeric.empty:
            return json.dumps({"error": "No numeric columns found"})
        
        corr = numeric.corr()
        
        # Heatmap com seaborn
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', 
                    square=True, linewidths=0.5, ax=ax, 
                    cbar_kws={"shrink": 0.8})
        ax.set_title("Correlation Matrix", fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        path = _save_plot(fig, prefix="corr")
        logger.info(f"Correlation matrix created for {len(corr.columns)} columns")
        return json.dumps({"corr": corr.to_json(), "plot_path": path})
    except Exception as e:
        logger.error(f"Error in correlation_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def outliers_tool(params: str) -> str:
    """Detecta outliers usando método IQR ou Z-score. Params: column=Amount, method=iqr"""
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        column = get_param(params_dict, "column", None)
        method = get_param(params_dict, "method", "iqr")
        
        if not column:
            return json.dumps({"error": "column parameter required"})
        
        exists, error_msg = validate_column_exists(df, column)
        if not exists:
            return json.dumps({"error": error_msg})
        
        if not is_numeric_dtype(df[column]):
            return json.dumps({"error":"column not numeric"})
        
        s = df[column].dropna()
        
        if method == "iqr":
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            low = q1 - 1.5*iqr
            high = q3 + 1.5*iqr
            out = df[(df[column] < low) | (df[column] > high)][[column]].to_dict(orient="records")
            logger.info(f"IQR outliers detected in {column}: {len(out)} outliers")
            return json.dumps({"method":"iqr","count":len(out),"outliers": out[:100]})  # Limit output
        else:
            # zscore
            z = (s - s.mean())/s.std()
            out_idx = z[abs(z) > 3].index
            out = df.loc[out_idx, [column]].to_dict(orient="records")
            logger.info(f"Z-score outliers detected in {column}: {len(out)} outliers")
            return json.dumps({"method":"zscore","count":len(out),"outliers": out[:100]})
    except Exception as e:
        logger.error(f"Error in outliers_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def clustering_tool(params: str) -> str:
    """Executa clustering K-means nos dados. Params: method=kmeans, n_clusters=3, columns=col1|col2|col3"""
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        method = get_param(params_dict, "method", "kmeans")
        n_clusters = get_param(params_dict, "n_clusters", 3, int)
        cols = params_dict.get("columns", "").split("|") if "columns" in params_dict else None
        
        if not cols:
            numeric = df.select_dtypes(include=[np.number]).columns.tolist()
            cols = numeric[:min(6, len(numeric))]
        
        data = df[cols].dropna()
        if data.empty:
            return json.dumps({"error":"no numeric data for clustering"})
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(data.values)
        centers = kmeans.cluster_centers_.tolist()
        counts = {int(i): int((kmeans.labels_==i).sum()) for i in range(n_clusters)}
        
        logger.info(f"K-means clustering: {n_clusters} clusters on {len(cols)} columns")
        return json.dumps({
            "method":"kmeans",
            "n_clusters":n_clusters,
            "centers":centers,
            "counts":counts,
            "columns":cols
        })
    except Exception as e:
        logger.error(f"Error in clustering_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def time_trend_tool(params: str) -> str:
    """
    Detecta padrões temporais em colunas do tipo tempo.
    params: "column=Time, target=Amount, freq=mean"
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error": "No dataframe loaded."})

    try:
        params_dict = parse_tool_params(params)
        column = get_param(params_dict, "column", "Time")
        target = get_param(params_dict, "target", None)
        freq = get_param(params_dict, "freq", "mean")

        if column not in df.columns:
            return json.dumps({"error": f"{column} not in dataframe"})
        
        if target and target not in df.columns:
            return json.dumps({"error": f"{target} not in dataframe"})

        if target:
            grouped = df.groupby(column)[target].agg(freq)
            fig, ax = plt.subplots(figsize=(12, 6))
            grouped.plot(ax=ax, color='steelblue', linewidth=2)
            ax.set_title(f"Time trend of {target} grouped by {freq}", fontsize=14, fontweight='bold')
            ax.set_xlabel(column, fontsize=12)
            ax.set_ylabel(target, fontsize=12)
            ax.grid(alpha=0.3)
            path = _save_plot(fig, prefix="time-trend")
            logger.info(f"Time trend plot created: {target} by {column}")
            return json.dumps({"message": "Time trend generated", "plot_path": path})
        else:
            counts = df[column].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(12, 6))
            counts.plot(ax=ax, color='steelblue', linewidth=2)
            ax.set_title(f"Frequency over time for {column}", fontsize=14, fontweight='bold')
            ax.grid(alpha=0.3)
            path = _save_plot(fig, prefix="time-trend")
            logger.info(f"Time frequency plot created for {column}")
            return json.dumps({"message": "Time frequency generated", "plot_path": path})
    except Exception as e:
        logger.error(f"Error in time_trend_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def frequency_tool(params: str) -> str:
    """
    Mostra os valores mais frequentes e menos frequentes de uma coluna.
    params: "column=Amount, top=10"
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        column = get_param(params_dict, "column", None)
        top = get_param(params_dict, "top", 10, int)
        
        if not column:
            return json.dumps({"error": "column parameter required"})
        
        if column not in df.columns:
            return json.dumps({"error":"column not found"})
        
        freq = df[column].value_counts()
        head = freq.head(top).to_dict()
        tail = freq.tail(top).to_dict()
        
        logger.info(f"Frequency analysis for {column}, top={top}")
        return json.dumps({"most_frequent": head, "least_frequent": tail})
    except Exception as e:
        logger.error(f"Error in frequency_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def crosstab_tool(params: str) -> str:
    """
    Cria tabela cruzada entre duas colunas.
    params: "col1=Class, col2=Amount"
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        col1 = get_param(params_dict, "col1", None)
        col2 = get_param(params_dict, "col2", None)
        
        if not col1 or not col2:
            return json.dumps({"error": "col1 and col2 parameters required"})
        
        if col1 not in df.columns or col2 not in df.columns:
            return json.dumps({"error":"col1 or col2 not found"})
        
        ct = pd.crosstab(df[col1], df[col2])
        logger.info(f"Crosstab created: {col1} x {col2}")
        return ct.to_json()
    except Exception as e:
        logger.error(f"Error in crosstab_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def central_tendency_tool(params: str) -> str:
    """
    Calcula média, mediana e moda de uma coluna.
    params: "column=Amount"
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        column = get_param(params_dict, "column", None)
        
        if not column:
            return json.dumps({"error": "column parameter required"})
        
        if column not in df.columns:
            return json.dumps({"error":"column not found"})
        
        series = df[column].dropna()
        mode = series.mode().iloc[0] if not series.mode().empty else None
        
        result = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "mode": safe_json_convert(mode)
        }
        
        logger.info(f"Central tendency calculated for {column}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in central_tendency_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def variability_tool(params: str) -> str:
    """
    Calcula variância, desvio padrão e coeficiente de variação.
    params: "column=Amount"
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        column = get_param(params_dict, "column", None)
        
        if not column:
            return json.dumps({"error": "column parameter required"})
        
        if column not in df.columns:
            return json.dumps({"error":"column not found"})
        
        series = df[column].dropna()
        result = {
            "variance": float(series.var()),
            "std_dev": float(series.std()),
            "cv": float(series.std() / series.mean()) if series.mean() != 0 else None
        }
        
        logger.info(f"Variability calculated for {column}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in variability_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def range_tool(params: str) -> str:
    """
    Retorna o intervalo (min, max) de uma coluna.
    params: "column=Amount"
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        params_dict = parse_tool_params(params)
        column = get_param(params_dict, "column", None)
        
        if not column:
            return json.dumps({"error": "column parameter required"})
        
        if column not in df.columns:
            return json.dumps({"error":"column not found"})
        
        series = df[column].dropna()
        result = {"min": float(series.min()), "max": float(series.max())}
        
        logger.info(f"Range calculated for {column}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in range_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def class_balance_tool(dummy: str) -> str:
    """
    Mostra o balanceamento das classes se existir coluna 'Class'.
    """
    df = get_dataframe()
    if df is None:
        return json.dumps({"error":"No dataframe loaded"})
    
    try:
        if "Class" not in df.columns:
            return json.dumps({"error":"No 'Class' column found"})
        
        counts = df["Class"].value_counts(normalize=True).to_dict()
        logger.info("Class balance calculated")
        return json.dumps({"class_balance": counts})
    except Exception as e:
        logger.error(f"Error in class_balance_tool: {e}")
        return json.dumps({"error": str(e)})

@tool
def conclusion_tool(dummy: str) -> str:
    """
    Gera uma conclusão automática baseada nos últimos resultados.
    Integra com memória para resumir insights.
    """
    df = get_dataframe()
    if df is None:
        return "Conclusão: Nenhum dataset foi carregado para análise."
    
    try:
        # Análise automática básica
        num_rows = len(df)
        num_cols = len(df.columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        missing_summary = {col: df[col].isna().sum() for col in df.columns if df[col].isna().sum() > 0}
        duplicates = df.duplicated().sum()
        
        conclusion = f"""
## 📊 Conclusão Automática da Análise

### Dataset Overview
- **Dimensões**: {num_rows} linhas × {num_cols} colunas
- **Colunas numéricas**: {len(numeric_cols)}
- **Valores ausentes**: {len(missing_summary)} colunas com missing values
- **Duplicatas**: {duplicates} linhas duplicadas ({round(duplicates/num_rows*100, 2)}%)

### Principais Observações
"""
        
        # Outliers em colunas numéricas
        for col in numeric_cols[:3]:  # Primeiras 3 colunas numéricas
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)]
            if len(outliers) > 0:
                conclusion += f"\n- **{col}**: {len(outliers)} outliers detectados ({round(len(outliers)/num_rows*100, 2)}%)"
        
        logger.info("Auto conclusion generated")
        return conclusion
        
    except Exception as e:
        logger.error(f"Error in conclusion_tool: {e}")
        return f"Erro ao gerar conclusão: {str(e)}"
