import os
import pandas as pd
from tabulate import tabulate

def list_files(file_type):
    """
    Lista los archivos disponibles en el directorio actual con la extensión especificada.
    """
    return [f for f in os.listdir('.') if f.endswith(f'.{file_type}')]

def validate_files_exist():
    """
    Valida si hay archivos .csv o .xlsx disponibles en el directorio actual.
    """
    csv_files = list_files('csv')
    xlsx_files = list_files('xlsx')

    if not csv_files and not xlsx_files:
        print("Error: No se encontraron archivos .csv ni .xlsx en el directorio actual.")
        print("Por favor, agregá los archivos necesarios y ejecutá el programa nuevamente.")
        exit(1)

    print("\nArchivos disponibles:")
    if csv_files:
        print(f"  Archivos .csv: {', '.join(csv_files)}")
    if xlsx_files:
        print(f"  Archivos .xlsx: {', '.join(xlsx_files)}")

    return csv_files, xlsx_files

def check_empty_files(files, file_type):
    """
    Revisa si alguno de los archivos especificados está vacío y lo informa.
    """
    empty_files = []
    for file in files:
        try:
            if file_type == 'csv':
                df = pd.read_csv(file)
            elif file_type == 'xlsx':
                df = pd.read_excel(file, engine='openpyxl')
            if df.empty:
                empty_files.append(file)
        except Exception:
            pass
    return empty_files

def read_file(file_path, file_type, sheet_name=None):
    """
    Función para leer un archivo y reemplazar valores NaN con 'Vacío'.
    """
    try:
        if file_type == 'xlsx':
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        elif file_type == 'csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Tipo de archivo no soportado. Solo .csv y .xlsx son válidos.")
        
        # Reemplazar NaN con "Vacío"
        df.fillna("Vacío", inplace=True)
        return df
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado. Verificá la ruta.")
        return None
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    except Exception as e:
        print(f"Error inesperado al leer el archivo: {e}")
        return None

def get_file_type(csv_files, xlsx_files):
    """
    Pregunta al usuario el tipo de archivo y valida la entrada.
    """
    while True:
        file_type = input("¿El archivo es .csv o .xlsx? ").strip().lower()
        if file_type == 'csv' and not csv_files:
            print("No hay archivos .csv disponibles. Intentá con otro tipo.")
        elif file_type == 'xlsx' and not xlsx_files:
            print("No hay archivos .xlsx disponibles. Intentá con otro tipo.")
        elif file_type in ['csv', 'xlsx']:
            return file_type
        else:
            print("Entrada inválida. Solo se permiten 'csv' o 'xlsx'.")

def get_file_name(file_type):
    """
    Pregunta al usuario el nombre del archivo y verifica que exista.
    """
    while True:
        file_name = input(f"Ingresá el nombre del archivo {file_type} (sin extensión): ").strip()
        full_path = f"{file_name}.{file_type}"
        if os.path.isfile(full_path):
            return full_path
        print(f"El archivo '{full_path}' no existe. Verificá el nombre e intentá nuevamente.")

def get_column_name(df, file_name):
    """
    Pide al usuario una columna válida de un DataFrame.
    """
    while True:
        print(f"\nColumnas disponibles en {file_name}: {list(df.columns)}")
        col_name = input(f"Ingresá el nombre de la columna de {file_name} que querés usar: ").strip()
        if col_name in df.columns:
            return col_name
        print(f"La columna '{col_name}' no existe en {file_name}. Intentá nuevamente.")

def compare_specific_columns(file1, file2, file_type1, file_type2, sheet_name1=None, sheet_name2=None):
    """
    Compara columnas específicas entre dos archivos.
    """
    while True:
        # Leer archivos
        df1 = read_file(file1, file_type1, sheet_name1)
        df2 = read_file(file2, file_type2, sheet_name2)
        
        if df1 is None or df2 is None:
            print("No se pudieron leer uno o ambos archivos. Intentá nuevamente.\n")
            continue
        
        # Obtener columnas válidas para comparar
        col1 = get_column_name(df1, file1)
        col2 = get_column_name(df2, file2)

        # Comparar columnas
        print(f"\n--- Comparando columna '{col1}' de {file1} con columna '{col2}' de {file2} ---")
        min_rows = min(len(df1), len(df2))
        differences = []

        for i in range(min_rows):
            val1 = df1.at[i, col1]
            val2 = df2.at[i, col2]
            if val1 != val2:
                differences.append({"Fila": i + 1, f"{file1} ({col1})": val1, f"{file2} ({col2})": val2})

        # Mostrar resultados
        if differences:
            print("\nDiferencias encontradas:")
            print(tabulate(differences, headers="keys", tablefmt="fancy_grid"))
        else:
            print("\n✅ No se encontraron diferencias en las columnas seleccionadas.")
        
        # Preguntar si el usuario desea realizar otra comparación
        retry = input("\n¿Querés comparar otra columna? (s/n): ").strip().lower()
        if retry != 's':
            print("Finalizando el programa. ¡Gracias por usar el comparador!")
            break

# Uso del script
if __name__ == "__main__":
    print("Bienvenido al comparador de archivos.\n")
    
    # Validar existencia de archivos
    csv_files, xlsx_files = validate_files_exist()

    # Informar sobre archivos vacíos
    empty_csv_files = check_empty_files(csv_files, 'csv')
    empty_xlsx_files = check_empty_files(xlsx_files, 'xlsx')

    if empty_csv_files:
        print(f"\nArchivos .csv vacíos: {', '.join(empty_csv_files)}")
    if empty_xlsx_files:
        print(f"\nArchivos .xlsx vacíos: {', '.join(empty_xlsx_files)}")

    while True:
        # Obtener información del primer archivo
        file_type1 = get_file_type(csv_files, xlsx_files)
        file1 = get_file_name(file_type1)

        # Obtener información del segundo archivo
        file_type2 = get_file_type(csv_files, xlsx_files)
        file2 = get_file_name(file_type2)

        # Pedir nombres de hojas si es necesario
        sheet1 = None
        sheet2 = None
        if file_type1 == 'xlsx':
            sheet1 = input("Ingresá el nombre de la hoja del primer archivo (o Enter para usar la primera): ").strip() or None
        if file_type2 == 'xlsx':
            sheet2 = input("Ingresá el nombre de la hoja del segundo archivo (o Enter para usar la primera): ").strip() or None

        # Comparar columnas específicas
        compare_specific_columns(file1, file2, file_type1, file_type2, sheet1, sheet2)

        # Preguntar si el usuario desea realizar otra comparación
        restart = input("\n¿Querés cargar otros archivos para comparar? (s/n): ").strip().lower()
        if restart != 's':
            print("Finalizando el programa. ¡Gracias por usar el comparador!")
            break
