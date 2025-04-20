import pandas as pd
import numpy as np


datos = pd.read_excel('Datos_soho-lasco.xlsx')
datos.columns = datos.columns.str.strip()


cols_numericas = ['LinearSpeed [km/s]', 'AngularWidth [deg]']
for col in cols_numericas:
    if col in datos.columns:
        datos[col] = pd.to_numeric(datos[col], errors='coerce')
    else:
        print(f"Advertencia: Columna {col} no encontrada")

# 5. Definir rangos (ahora con etiquetas incluidas)
rangos_velocidad = [
    (500, 599, "500-599 km/s"),
    (600, 699, "600-699 km/s"),
    (700, 799, "700-799 km/s"),
    (800, 900, "800-900 km/s"),
    (901, np.inf, ">900 km/s")
]

rangos_anchura = [
    (45, 60, "45-60°"),
    (61, 90, "61-90°"),
    (91, np.inf, ">90°")
]

# 6. Crear lista para resultados
resultados = []

# 7. Realizar el análisis
for v_min, v_max, v_label in rangos_velocidad:
    for a_min, a_max, a_label in rangos_anchura:
        # Filtrar por velocidad
        if np.isinf(v_max):
            filtro_vel = (datos['LinearSpeed [km/s]'] >= v_min)
        else:
            filtro_vel = (datos['LinearSpeed [km/s]'] >= v_min) & (datos['LinearSpeed [km/s]'] <= v_max)
        
        # Filtrar por anchura
        if np.isinf(a_max):
            filtro_anchura = (datos['AngularWidth [deg]'] >= a_min)
        else:
            filtro_anchura = (datos['AngularWidth [deg]'] >= a_min) & (datos['AngularWidth [deg]'] <= a_max)
        
        # Contar CME
        cantidad = datos[filtro_vel & filtro_anchura].shape[0]
        
        resultados.append({
            'Rango Velocidad': v_label,
            'Rango Anchura': a_label,
            'Cantidad CME': cantidad
        })

# 8. Crear DataFrame de resultados
df_resultados = pd.DataFrame(resultados)

# 9. Mostrar como tabla pivot
tabla_resumen = df_resultados.pivot(
    index='Rango Velocidad',
    columns='Rango Anchura',
    values='Cantidad CME'
)

print("\nResumen de CME por rangos:")
print(tabla_resumen.fillna(0).astype(int))  # Mostrar 0 en lugar de NaN

# 10. Guardar resultados
df_resultados.to_excel('resumen_cme_detallado.xlsx', index=False)
tabla_resumen.to_excel('resumen_cme_pivot.xlsx')

print("\nResultados guardados en:")
print("- resumen_cme_detallado.xlsx")
print("- resumen_cme_pivot.xlsx")

# Visualizar datos


import matplotlib.pyplot as plt
from matplotlib import cm

# Cargar los datos procesados
df_resultados = pd.read_excel('resumen_cme_pivot.xlsx', index_col=0)

# 1. Heatmap con matplotlib
plt.figure(figsize=(10, 6))
c = plt.pcolor(df_resultados.fillna(0).astype(int), 
             cmap='YlOrRd', 
             edgecolors='white', 
             linewidths=1)

plt.colorbar(c, label='Número de CME')
plt.title("Distribución de CME por Velocidad y Anchura Angular", pad=20)
plt.xlabel("Rango de Anchura Angular (grados)")
plt.ylabel("Rango de Velocidad (km/s)")

# Añadir etiquetas
for y in range(df_resultados.shape[0]):
    for x in range(df_resultados.shape[1]):
        plt.text(x + 0.5, y + 0.5, f"{df_resultados.iloc[y, x]}",
                horizontalalignment='center',
                verticalalignment='center')

plt.xticks(np.arange(0.5, len(df_resultados.columns), 1), df_resultados.columns)
plt.yticks(np.arange(0.5, len(df_resultados.index), 1), df_resultados.index)
plt.tight_layout()
plt.savefig('heatmap_cme.png', dpi=300)
plt.show()

# 2. Gráfico de Barras Agrupadas
df_melted = df_resultados.reset_index().melt(id_vars='Rango Velocidad', 
                                          var_name='Anchura Angular', 
                                          value_name='Conteo')

plt.figure(figsize=(12, 7))
width = 0.2  # Ancho de las barras
x = np.arange(len(df_resultados.index))

for i, (angulo, grupo) in enumerate(df_melted.groupby('Anchura Angular')):
    plt.bar(x + i*width, grupo['Conteo'], width, label=angulo, edgecolor='black')

plt.title("Conteo de CME por Rangos de Velocidad y Ancho angular", pad=20)
plt.xlabel("Rango de Velocidad (km/s)", labelpad=10)
plt.ylabel("Número de CME", labelpad=10)
plt.legend(title='Anchura Angular', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(x + width, df_resultados.index)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('barras_cme.png', dpi=300, bbox_inches='tight')
plt.show()

print("Gráficos guardados como 'heatmap_cme.png' y 'barras_cme.png'")