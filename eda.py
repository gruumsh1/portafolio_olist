import pandas as pd

def cargar_datos():
    # Ajusta las rutas según dónde hayas guardado los archivos descomprimidos
    orders = pd.read_csv('olist_orders_dataset.csv')
    items = pd.read_csv('olist_order_items_dataset.csv')
    reviews = pd.read_csv('olist_order_reviews_dataset.csv')
    
    print("¡Datos cargados exitosamente!")
    print(f"Órdenes: {orders.shape[0]} filas")
    print(f"Artículos: {items.shape[0]} filas")
    print(f"Reseñas: {reviews.shape[0]} filas")
    
    return orders, items, reviews

if __name__ == "__main__":
    orders, items, reviews = cargar_datos()