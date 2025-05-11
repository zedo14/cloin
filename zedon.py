import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import random
import time

class Product:
    def __init__(self, id, name, price, category):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.views = 0

class RecommendationNode:
    def __init__(self, product):
        self.product = product
        self.left = None
        self.right = None
        self.height = 1

class AVLRecommendationTree:
    def __init__(self):
        self.root = None
    
    def insert(self, root, product):
        if not root:
            return RecommendationNode(product)
        
        if product.views < root.product.views:
            root.left = self.insert(root.left, product)
        else:
            root.right = self.insert(root.right, product)
        
        root.height = 1 + max(self.get_height(root.left), 
                            self.get_height(root.right))
        
        balance = self.get_balance(root)
        
        # Left Left
        if balance > 1 and product.views < root.left.product.views:
            return self.right_rotate(root)
        
        # Right Right
        if balance < -1 and product.views >= root.right.product.views:
            return self.left_rotate(root)
        
        # Left Right
        if balance > 1 and product.views >= root.left.product.views:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        
        # Right Left
        if balance < -1 and product.views < root.right.product.views:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)
        
        return root
    
    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        z.height = 1 + max(self.get_height(z.left), 
                         self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), 
                         self.get_height(y.right))
        
        return y
    
    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        z.height = 1 + max(self.get_height(z.left), 
                         self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), 
                         self.get_height(y.right))
        
        return y
    
    def get_height(self, root):
        if not root:
            return 0
        return root.height
    
    def get_balance(self, root):
        if not root:
            return 0
        return self.get_height(root.left) - self.get_height(root.right)
    
    def in_order_traversal(self, root, result):
        if root:
            self.in_order_traversal(root.right, result)
            result.append(root.product)
            self.in_order_traversal(root.left, result)

class OnlineShoppingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced E-Commerce Platform")
        self.root.geometry("1000x700")
        
        # Initialize data structures
        self.products = []
        self.initialize_products()
        self.recommendation_tree = AVLRecommendationTree()
        self.order_queue = deque()
        
        # Create UI
        self.create_widgets()
        
        # Track viewed products for recommendations
        self.viewed_products = []
        
    def initialize_products(self):
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
        for i in range(1, 101):
            category = random.choice(categories)
            self.products.append(
                Product(i, f"{category[:-1]} Product {i}", 
                       round(random.uniform(10, 500), 2), category)
            )
    
    def create_widgets(self):
        # Main frames
        self.search_frame = ttk.LabelFrame(self.root, text="Product Search", padding=10)
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.results_frame = ttk.LabelFrame(self.root, text="Search Results", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.recommendations_frame = ttk.LabelFrame(self.root, text="Recommendations", padding=10)
        self.recommendations_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Search components
        ttk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_entry = ttk.Entry(self.search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.search_frame, text="Category:").grid(row=0, column=2, padx=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.search_frame, 
                                            textvariable=self.category_var,
                                            values=["All"] + list(set(p.category for p in self.products)))
        self.category_dropdown.current(0)
        self.category_dropdown.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.search_frame, text="Sort by:").grid(row=0, column=4, padx=5)
        self.sort_var = tk.StringVar()
        self.sort_dropdown = ttk.Combobox(self.search_frame, 
                                         textvariable=self.sort_var,
                                         values=["Name", "Price (Low to High)", "Price (High to Low)"])
        self.sort_dropdown.current(0)
        self.sort_dropdown.grid(row=0, column=5, padx=5)
        
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_products)
        self.search_button.grid(row=0, column=6, padx=5)
        
        # Results treeview
        self.results_tree = ttk.Treeview(self.results_frame, columns=("ID", "Name", "Price", "Category"), show="headings")
        self.results_tree.heading("ID", text="ID")
        self.results_tree.heading("Name", text="Name")
        self.results_tree.heading("Price", text="Price ($)")
        self.results_tree.heading("Category", text="Category")
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        self.results_tree.bind("<Double-1>", self.view_product_details)
        
        # Recommendations treeview
        self.recommendations_tree = ttk.Treeview(self.recommendations_frame, columns=("ID", "Name", "Price", "Category", "Views"), show="headings")
        self.recommendations_tree.heading("ID", text="ID")
        self.recommendations_tree.heading("Name", text="Name")
        self.recommendations_tree.heading("Price", text="Price ($)")
        self.recommendations_tree.heading("Category", text="Category")
        self.recommendations_tree.heading("Views", text="Views")
        self.recommendations_tree.pack(fill=tk.BOTH, expand=True)
        
        # Order processing button
        self.process_order_btn = ttk.Button(self.root, text="Process Next Order", command=self.process_order)
        self.process_order_btn.pack(pady=5)
        
        # Show all products initially
        self.display_products(self.products)
    
    def search_products(self):
        query = self.search_entry.get().lower()
        category = self.category_var.get()
        sort_option = self.sort_var.get()
        
        # Simple linear search (could be optimized with more advanced structures)
        results = []
        for product in self.products:
            if (query in product.name.lower() or not query) and \
               (product.category == category or category == "All"):
                results.append(product)
        
        # Sorting
        if sort_option == "Price (Low to High)":
            results.sort(key=lambda x: x.price)
        elif sort_option == "Price (High to Low)":
            results.sort(key=lambda x: -x.price)
        else:  # Name
            results.sort(key=lambda x: x.name)
        
        self.display_products(results)
    
    def display_products(self, products):
        # Clear current results
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)
        
        # Add new results
        for product in products:
            self.results_tree.insert("", tk.END, 
                                   values=(product.id, product.name, 
                                           f"{product.price:.2f}", product.category))
    
    def view_product_details(self, event):
        item = self.results_tree.selection()[0]
        product_id = int(self.results_tree.item(item, "values")[0])
        
        # Find product
        product = next(p for p in self.products if p.id == product_id)
        
        # Increment view count
        product.views += 1
        self.viewed_products.append(product)
        
        # Show details
        messagebox.showinfo("Product Details", 
                          f"Name: {product.name}\nPrice: ${product.price:.2f}\nCategory: {product.category}\nViews: {product.views}")
        
        # Update recommendations
        self.update_recommendations()
        
        # Add to order queue (simulate purchase)
        self.order_queue.append(product)
        messagebox.showinfo("Order Placed", f"{product.name} added to your cart!")
    
    def update_recommendations(self):
        # Rebuild recommendation tree based on view counts
        self.recommendation_tree = AVLRecommendationTree()
        for product in self.products:
            if product.views > 0:
                self.recommendation_tree.root = self.recommendation_tree.insert(
                    self.recommendation_tree.root, product)
        
        # Get recommendations (most viewed products)
        recommendations = []
        if self.recommendation_tree.root:
            self.recommendation_tree.in_order_traversal(self.recommendation_tree.root, recommendations)
        
        # Display top 5 recommendations
        for row in self.recommendations_tree.get_children():
            self.recommendations_tree.delete(row)
        
        for product in recommendations[:5]:
            self.recommendations_tree.insert("", tk.END, 
                                            values=(product.id, product.name, 
                                                    f"{product.price:.2f}", 
                                                    product.category, product.views))
    
    def process_order(self):
        if not self.order_queue:
            messagebox.showinfo("Order Queue", "No orders to process!")
            return
        
        # Process FIFO (queue behavior)
        product = self.order_queue.popleft()
        messagebox.showinfo("Order Processed", 
                           f"Order for {product.name} has been processed!\n"
                           f"Total: ${product.price:.2f}\n"
                           f"Estimated delivery: {time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400 * 3))}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OnlineShoppingApp(root)
    root.mainloop()