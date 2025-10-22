import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2 import sql
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import random
import string
import pandas as pd
from datetime import datetime
import os
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "inventory_db",
    "user": "postgres",
    "password": "sr@403"
}

class LoginPage:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.configure(bg="#4b9783")
        
        container = tk.Frame(self.root, bg="#4b9783")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        profile_frame = tk.Frame(container, bg="#7db3a3", width=150, height=150)
        profile_frame.pack(pady=(0, 30))
        profile_frame.pack_propagate(False)
        
        tk.Label(profile_frame, text="👤", font=("Arial", 80), bg="#7db3a3", fg="white").pack(expand=True)
        
        role_frame = tk.Frame(container, bg="white", relief=tk.RAISED, bd=2)
        role_frame.pack(pady=10, padx=20)
        
        self.role_var = tk.StringVar(value="Admin")
        
        admin_rb = tk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value="Admin",
                                 font=("Arial", 14), bg="white", selectcolor="#4b9783",
                                 activebackground="white", cursor="hand2")
        admin_rb.pack(side=tk.LEFT, padx=30, pady=15)
        
        tk.Frame(role_frame, width=2, bg="#ccc").pack(side=tk.LEFT, fill=tk.Y, pady=10)
        
        employee_rb = tk.Radiobutton(role_frame, text="Employee", variable=self.role_var, value="Employee",
                                    font=("Arial", 14), bg="white", selectcolor="#4b9783",
                                    activebackground="white", cursor="hand2")
        employee_rb.pack(side=tk.LEFT, padx=30, pady=15)
        
        username_frame = tk.Frame(container, bg="white", relief=tk.RAISED, bd=2)
        username_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(username_frame, text="👤", font=("Arial", 20), bg="white", fg="#4b9783").pack(side=tk.LEFT, padx=10)
        self.username_entry = tk.Entry(username_frame, font=("Arial", 14), bg="white", bd=0, fg="#666")
        self.username_entry.insert(0, "Username")
        self.username_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=15, padx=5)
        
        password_frame = tk.Frame(container, bg="white", relief=tk.RAISED, bd=2)
        password_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(password_frame, text="🔒", font=("Arial", 20), bg="white", fg="#4b9783").pack(side=tk.LEFT, padx=10)
        self.password_entry = tk.Entry(password_frame, font=("Arial", 14), bg="white", bd=0, fg="#666", show="*")
        self.password_entry.insert(0, "Password")
        self.password_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=15, padx=5)
        
        options_frame = tk.Frame(container, bg="#4b9783")
        options_frame.pack(pady=15, fill=tk.X, padx=20)
        
        remember_frame = tk.Frame(options_frame, bg="#4b9783")
        remember_frame.pack(side=tk.LEFT)
        
        self.remember_var = tk.BooleanVar(value=True)
        tk.Checkbutton(remember_frame, text="Remember me", variable=self.remember_var,
                      font=("Arial", 11), bg="#4b9783", fg="white", selectcolor="#4b9783",
                      activebackground="#4b9783", activeforeground="white").pack()
        
        forgot_btn = tk.Button(options_frame, text="Forgot Password?", font=("Arial", 11, "italic"),
                              bg="#4b9783", fg="white", bd=0, cursor="hand2",
                              command=self.forgot_password)
        forgot_btn.pack(side=tk.RIGHT)
        
        login_btn = tk.Button(container, text="LOGIN", font=("Arial", 14, "bold"),
                            bg="#7db3a3", fg="white", width=25, height=2, bd=0,
                            cursor="hand2", command=self.login)
        login_btn.pack(pady=20)
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if username == "Username" or password == "Password":
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            
            if role == "Admin":
                if username == "sr" and password == "Admin@123":
                    self.on_login_success("Admin", username)
                else:
                    messagebox.showerror("Error", "Invalid admin credentials")
            else:
                cur.execute("SELECT employee_id, password FROM employees WHERE employee_id = %s", (username,))
                result = cur.fetchone()
                
                if result and result[1] == password:
                    self.on_login_success("Employee", username)
                else:
                    messagebox.showerror("Error", "Invalid employee credentials")
            
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            conn.close()
    
    def forgot_password(self):
        role = self.role_var.get()
        
        if role == "Employee":
            username = self.username_entry.get()
            if username == "Username" or not username:
                messagebox.showerror("Error", "Please enter your employee ID")
                return
            
            new_password = self.generate_password()
            
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    
                    cur.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (username,))
                    if not cur.fetchone():
                        messagebox.showerror("Error", "Employee ID not found")
                        cur.close()
                        conn.close()
                        return
                    
                    cur.execute("UPDATE employees SET password = %s WHERE employee_id = %s", 
                               (new_password, username))
                    
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS admin_notifications (
                            id SERIAL PRIMARY KEY,
                            type VARCHAR(50),
                            message TEXT,
                            employee_id VARCHAR(50),
                            new_password VARCHAR(50),
                            read BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    cur.execute("""
                        INSERT INTO admin_notifications (type, message, employee_id, new_password)
                        VALUES (%s, %s, %s, %s)
                    """, ('password_reset', f'Employee {username} requested password reset', username, new_password))
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    messagebox.showinfo("Success", "Password reset request sent to admin")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send request: {str(e)}")
                    if conn:
                        conn.close()
        else:
            self.admin_forgot_password()
    
    def admin_forgot_password(self):
        popup = tk.Toplevel(self.root)
        popup.title("Admin Password Recovery")
        popup.geometry("400x300")
        popup.configure(bg="white")
        
        tk.Label(popup, text="What's the last you remember?", font=("Arial", 12, "bold"),
                bg="white").pack(pady=20)
        
        tk.Label(popup, text="Enter any part of your password:", font=("Arial", 10),
                bg="white").pack(pady=5)
        
        remember_entry = tk.Entry(popup, font=("Arial", 12), width=30)
        remember_entry.pack(pady=10)
        
        def verify_and_reset():
            remembered = remember_entry.get()
            if len(remembered) >= 3 and remembered.lower() in "admin@123".lower():
                popup.destroy()
                self.show_password_reset()
            else:
                messagebox.showerror("Error", "Information doesn't match our records")
        
        tk.Button(popup, text="Verify", font=("Arial", 12), bg="#4b9783", fg="white",
                 width=15, cursor="hand2", command=verify_and_reset).pack(pady=20)
    
    def show_password_reset(self):
        popup = tk.Toplevel(self.root)
        popup.title("Reset Password")
        popup.geometry("400x300")
        popup.configure(bg="white")
        
        tk.Label(popup, text="Reset Admin Password", font=("Arial", 12, "bold"),
                bg="white").pack(pady=20)
        
        tk.Label(popup, text="New Password:", font=("Arial", 10), bg="white").pack(pady=5)
        new_pass_entry = tk.Entry(popup, font=("Arial", 12), width=30, show="*")
        new_pass_entry.pack(pady=5)
        
        tk.Label(popup, text="Retype New Password:", font=("Arial", 10), bg="white").pack(pady=5)
        retype_pass_entry = tk.Entry(popup, font=("Arial", 12), width=30, show="*")
        retype_pass_entry.pack(pady=5)
        
        def submit_reset():
            new_pass = new_pass_entry.get()
            retype_pass = retype_pass_entry.get()
            
            if new_pass != retype_pass:
                messagebox.showerror("Error", "Passwords don't match")
                return
            
            if len(new_pass) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters")
                return
            
            messagebox.showinfo("Success", "Password reset successfully!")
            popup.destroy()
        
        tk.Button(popup, text="Submit", font=("Arial", 12), bg="#4b9783", fg="white",
                 width=15, cursor="hand2", command=submit_reset).pack(pady=20)
    
    def generate_password(self):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(8))
    
    def get_db_connection(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect: {str(e)}")
            return None

class InventoryDashboard:
    def __init__(self, root, role, username):
        self.root = root
        self.role = role
        self.username = username
        self.current_page = "Dashboard"
        
        self.root.title("Inventory Management System")
        self.root.geometry("1366x768")
        self.root.configure(bg="#f5f5f5")
        
        self.data = self.fetch_data()
        self.notifications = self.check_notifications()
        
        # For inventory selection
        self.inventory_checkboxes = {}
        self.inventory_selection_mode = False
        
        # For employee selection
        self.employee_checkboxes = {}
        self.employee_selection_mode = False
        
        # For sales selection
        self.sales_checkboxes = {}
        self.sales_selection_mode = False
        
        #For Purchase selection
        self.purchase_checkboxes = {}
        self.purchase_selection_mode = False

        self.create_sidebar()
        self.create_main_area()
        self.show_dashboard()
    
    def get_db_connection(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect: {str(e)}")
            return None
    
    def fetch_data(self):
        conn = self.get_db_connection()
        if not conn:
            return self.get_dummy_data()
        
        try:
            cur = conn.cursor()
            
            cur.execute("SELECT COALESCE(SUM(quantity), 0) FROM products")
            total_products = cur.fetchone()[0] or 0
            
            cur.execute("SELECT COALESCE(SUM(quantity_sold), 0) FROM sales")
            total_sales = cur.fetchone()[0] or 0
            
            cur.execute("SELECT COALESCE(SUM(total_cost), 0) FROM purchases")
            total_purchases = cur.fetchone()[0] or 0
            
            cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales")
            total_revenue = cur.fetchone()[0] or 0
            
            cur.execute("SELECT COUNT(DISTINCT user_id) FROM users")
            total_customers = cur.fetchone()[0] or 0
            
            # Get available units (current inventory)
            cur.execute("SELECT COALESCE(SUM(quantity), 0) FROM products")
            available_units = cur.fetchone()[0] or 0
            
            # Get sold units
            cur.execute("SELECT COALESCE(SUM(quantity_sold), 0) FROM sales")
            sold_units = cur.fetchone()[0] or 0
            
            # Total original inventory = available + sold
            total_units = available_units + sold_units
            
            # If no data, set total to 1 to avoid division by zero
            if total_units == 0:
                total_units = 1
            
            cur.execute("""
                SELECT p.product_name, SUM(s.quantity_sold) as total_sold 
                FROM sales s
                JOIN products p ON s.product_id = p.product_id
                GROUP BY p.product_name 
                ORDER BY total_sold DESC 
                LIMIT 10
            """)
            top_products = cur.fetchall()
            
            # ===== FINANCIAL DATA - YEAR WISE WITH ALL 12 MONTHS =====
            from datetime import datetime
            current_year = datetime.now().year
            
            # Initialize month_names
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # Get expenses from purchases
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM purchase_date) as month_num,
                    SUM(total_cost) as expenses
                FROM purchases
                WHERE EXTRACT(YEAR FROM purchase_date) = %s
                GROUP BY EXTRACT(MONTH FROM purchase_date)
            """, (current_year,))
            
            expenses_data = {}
            for row in cur.fetchall():
                month_num = int(row[0])
                expenses = float(row[1]) if row[1] else 0
                expenses_data[month_num] = expenses
            
            # Get revenue from sales
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM sales_date) as month_num,
                    SUM(total_amount) as revenue
                FROM sales
                WHERE EXTRACT(YEAR FROM sales_date) = %s
                GROUP BY EXTRACT(MONTH FROM sales_date)
            """, (current_year,))
            
            revenue_data = {}
            for row in cur.fetchall():
                month_num = int(row[0])
                revenue = float(row[1]) if row[1] else 0
                revenue_data[month_num] = revenue
            
            # Create financial_data for all 12 months
            financial_data = []
            for month_num in range(1, 13):
                month_name = month_names[month_num - 1]
                expenses = expenses_data.get(month_num, 0)
                revenue = revenue_data.get(month_num, 0)
                financial_data.append((month_name, expenses, revenue))
            
            cur.close()
            conn.close()
            
            return {
                'total_products': total_products,
                'total_sales': total_sales,
                'total_purchases': total_purchases,
                'total_revenue': total_revenue,
                'total_customers': total_customers,
                'sold_units': sold_units,
                'available_units': available_units,
                'total_units': total_units,
                'top_products': top_products,
                'financial_data': financial_data  
            }
            
        except Exception as e:
            print(f"ERROR in fetch_data: {e}")  # Debug print
            if conn:
                conn.close()
            return self.get_dummy_data()
    
    def get_dummy_data(self):
        # Create dummy data with all 12 months set to 0
        financial_data = []
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month in month_names:
            financial_data.append((month, 0, 0))
        
        return {
            'total_products': 0,
            'total_sales': 0,
            'total_purchases': 0,
            'total_revenue': 0,
            'total_customers': 0,
            'sold_units': 0,
            'available_units': 0,
            'total_units': 1,
            'top_products': [],
            'financial_data': financial_data
        }

    def check_notifications(self):
        notifications = []
        
        if self.data['total_revenue'] < 10000:
            notifications.append("⚠️ Low Revenue Alert: Revenue is below target threshold")
        
        if self.data['total_sales'] < 5:
            notifications.append("⚠️ Low Sales: Sales count is critically low")
        
        if self.data['total_customers'] == 0:
            notifications.append("⚠️ No Customers: Customer acquisition needed")
        
        if self.role == "Admin":
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    
                    # Password reset notifications
                    cur.execute("""
                        SELECT message, new_password, employee_id 
                        FROM admin_notifications 
                        WHERE read = false
                    """)
                    admin_notifs = cur.fetchall()
                    for notif in admin_notifs:
                        notifications.append(f"🔑 {notif[0]}\n   New Password: {notif[1]} for Employee: {notif[2]}")
                    
                    # Contact issue notifications
                    cur.execute("""
                        SELECT email, issue, submitted_by, created_at 
                        FROM contact_issues 
                        WHERE read = false AND status = 'Pending'
                        ORDER BY created_at DESC
                    """)
                    contact_issues = cur.fetchall()
                    for issue in contact_issues:
                        issue_preview = issue[1][:50] + "..." if len(issue[1]) > 50 else issue[1]
                        notifications.append(f"📧 Contact Issue from {issue[0]}\n   Submitted by: {issue[2]}\n   Issue: {issue_preview}")
                    
                    cur.close()
                    conn.close()
                except:
                    pass
        
        return notifications
    
    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="#4b9783", width=80)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        menu_items = [
            ("📊", "Dashboard"),
            ("📦", "Inventory"),
            ("💰", "Sales"),
            ("🛒", "Purchase"),
            ("🔧", "Maintenance")
        ]
        
        for icon, name in menu_items:
            btn = tk.Button(self.sidebar, text=icon, font=("Arial", 24),
                          bg="#4b9783", fg="white", bd=0, cursor="hand2",
                          activebackground="#3d7a6a", width=3, height=2,
                          command=lambda n=name: self.switch_page(n))
            btn.pack(pady=10)
    
    def create_main_area(self):
        # Create canvas for scrolling
        self.main_canvas = tk.Canvas(self.root, bg="#f5f5f5", highlightthickness=0)
        self.main_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.main_area = tk.Frame(self.main_canvas, bg="#f5f5f5")
        
        self.main_area.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_frame = self.main_canvas.create_window((0, 0), window=self.main_area, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Pack canvas and scrollbar
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # IMPORTANT: Bind canvas width to actual canvas width
        def on_canvas_configure(event):
            # Get the canvas width and update the window width
            canvas_width = event.width
            self.main_canvas.itemconfig(self.canvas_frame, width=canvas_width)
        
        self.main_canvas.bind('<Configure>', on_canvas_configure)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            self.main_canvas.unbind_all("<MouseWheel>")
        
        self.main_canvas.bind('<Enter>', _bind_mousewheel)
        self.main_canvas.bind('<Leave>', _unbind_mousewheel)


    def switch_page(self, page):
        self.current_page = page

        self.main_canvas.yview_moveto(0)
        
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Inventory":
            self.show_inventory()
        elif page == "Sales":
            self.show_sales()
        elif page == "Purchase":
            self.show_purchase()
        elif page == "Maintenance":
            self.show_contact()
    
    def create_header(self):
        header = tk.Frame(self.main_area, bg="white", height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        search_frame = tk.Frame(header, bg="white", relief=tk.RAISED, bd=1)
        search_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(search_frame, text="🔍", bg="white", fg="#4b9783", font=("Arial", 16)).pack(side=tk.LEFT, padx=10)
        
        search_entry = tk.Entry(search_frame, font=("Arial", 12), bg="white", bd=0, fg="#666")
        search_entry.insert(0, "search or command")
        search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind Enter key to search
        search_entry.bind("<Return>", lambda e: self.perform_search(search_entry.get()))
        
        # Clear placeholder on focus
        def on_focus_in(event):
            if search_entry.get() == "search or command":
                search_entry.delete(0, tk.END)
                search_entry.config(fg="black")
        
        def on_focus_out(event):
            if search_entry.get() == "":
                search_entry.insert(0, "search or command")
                search_entry.config(fg="#666")
        
        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
        
        right_frame = tk.Frame(header, bg="white")
        right_frame.pack(side=tk.RIGHT, padx=20)
        
        notif_btn = tk.Button(right_frame, text="🔔", font=("Arial", 18),
                             bg="white", fg="#4b9783", bd=0, cursor="hand2",
                             command=self.show_notifications)
        notif_btn.pack(side=tk.LEFT, padx=10)
        
        settings_btn = tk.Button(right_frame, text="⚙️", font=("Arial", 18),
                                bg="white", fg="#4b9783", bd=0, cursor="hand2",
                                command=self.show_settings)
        settings_btn.pack(side=tk.LEFT, padx=10)
        
        role_text = "Admin" if self.role == "Admin" else f"Employee"
        admin_label = tk.Label(right_frame, text=role_text, font=("Arial", 12, "bold"),
                              bg="white", fg="#333")
        admin_label.pack(side=tk.LEFT, padx=10)

    def perform_search(self, query):
        """Smart search across all pages"""
        if not query or query == "search or command":
            messagebox.showinfo("Search", "Please enter a search term")
            return
        
        query = query.lower().strip()
        
        # Define search keywords for each page
        page_keywords = {
            'Dashboard': ['dashboard', 'overview', 'home', 'summary', 'stats', 'statistics'],
            'Inventory': ['inventory', 'product', 'stock', 'item', 'goods', 'warehouse'],
            'Sales': ['sales', 'sell', 'sold', 'customer', 'order', 'revenue'],
            'Purchase': ['purchase', 'buy', 'bought', 'supplier', 'procurement', 'vendor'],
            'Maintenance': ['contact', 'help', 'support', 'issue', 'problem', 'maintenance']
        }
        
        # Check for page navigation keywords
        for page, keywords in page_keywords.items():
            if any(keyword in query for keyword in keywords):
                self.switch_page(page)
                # Perform specific search within the page
                self.search_within_page(page, query)
                return
        
        # If no page keyword found, search across all data
        self.global_search(query)
    
    def search_within_page(self, page, query):
        """Search within a specific page and filter results"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            results = []
            
            if page == 'Inventory':
                # Search products
                cur.execute("""
                    SELECT product_id, product_name, category, quantity, price 
                    FROM products 
                    WHERE LOWER(product_id) LIKE %s 
                       OR LOWER(product_name) LIKE %s 
                       OR LOWER(category) LIKE %s
                       OR LOWER(supplier) LIKE %s
                """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
                results = cur.fetchall()
                
                if results:
                    messagebox.showinfo("Search Results", 
                                      f"Found {len(results)} product(s) matching '{query}'")
                else:
                    messagebox.showinfo("Search Results", f"No products found matching '{query}'")
            
            elif page == 'Sales':
                # Search sales
                cur.execute("""
                    SELECT s.sales_id, s.product_id, s.quantity_sold, s.total_amount, u.user_name
                    FROM sales s
                    LEFT JOIN users u ON s.user_id = u.user_id
                    WHERE LOWER(s.sales_id) LIKE %s 
                       OR LOWER(s.product_id) LIKE %s 
                       OR LOWER(s.employee_id) LIKE %s
                       OR LOWER(s.user_id) LIKE %s
                """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
                results = cur.fetchall()
                
                if results:
                    messagebox.showinfo("Search Results", 
                                      f"Found {len(results)} sale(s) matching '{query}'")
                else:
                    messagebox.showinfo("Search Results", f"No sales found matching '{query}'")
            
            elif page == 'Purchase':
                # Search purchases
                cur.execute("""
                    SELECT purchase_id, product_id, quantity_purchased, total_cost, supplier
                    FROM purchases 
                    WHERE LOWER(purchase_id) LIKE %s 
                       OR LOWER(product_id) LIKE %s 
                       OR LOWER(supplier) LIKE %s
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                results = cur.fetchall()
                
                if results:
                    messagebox.showinfo("Search Results", 
                                      f"Found {len(results)} purchase(s) matching '{query}'")
                else:
                    messagebox.showinfo("Search Results", f"No purchases found matching '{query}'")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search: {str(e)}")
            if conn:
                conn.close()
    
    def global_search(self, query):
        """Search across all pages when no specific page keyword is found"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            search_results = []
            
            # Search in products
            cur.execute("""
                SELECT 'Product' as type, product_id as id, product_name as name, 'Inventory' as page
                FROM products 
                WHERE LOWER(product_id) LIKE %s OR LOWER(product_name) LIKE %s
                LIMIT 5
            """, (f'%{query}%', f'%{query}%'))
            search_results.extend(cur.fetchall())
            
            # Search in sales
            cur.execute("""
                SELECT 'Sale' as type, sales_id as id, product_id as name, 'Sales' as page
                FROM sales 
                WHERE LOWER(sales_id) LIKE %s OR LOWER(product_id) LIKE %s
                LIMIT 5
            """, (f'%{query}%', f'%{query}%'))
            search_results.extend(cur.fetchall())
            
            # Search in purchases
            cur.execute("""
                SELECT 'Purchase' as type, purchase_id as id, product_id as name, 'Purchase' as page
                FROM purchases 
                WHERE LOWER(purchase_id) LIKE %s OR LOWER(product_id) LIKE %s
                LIMIT 5
            """, (f'%{query}%', f'%{query}%'))
            search_results.extend(cur.fetchall())
            
            cur.close()
            conn.close()
            
            if search_results:
                # Show results in a popup
                self.show_search_results(query, search_results)
            else:
                messagebox.showinfo("Search Results", f"No results found for '{query}'")
                
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search: {str(e)}")
            if conn:
                conn.close()
    
    def show_search_results(self, query, results):
        """Display search results in a popup window"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Search Results: {query}")
        popup.geometry("600x400")
        popup.configure(bg="white")
        
        tk.Label(popup, text=f"Search Results for '{query}'", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=20)
        
        # Create results table
        table_frame = tk.Frame(popup, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Type", "ID", "Name", "Page")
        results_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            results_tree.heading(col, text=col)
            results_tree.column(col, width=140)
        
        for result in results:
            results_tree.insert("", tk.END, values=result)
        
        scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=results_tree.yview)
        results_tree.configure(yscrollcommand=scrollbar.set)
        
        results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Navigate to page button
        def go_to_page():
            selection = results_tree.selection()
            if selection:
                item = results_tree.item(selection[0])
                page = item['values'][3]
                self.switch_page(page)
                popup.destroy()
        
        tk.Button(popup, text="Go to Page", font=("Arial", 12),
                 bg="#4b9783", fg="white", width=15, cursor="hand2",
                 command=go_to_page).pack(pady=20)
        
        results_tree.bind("<Double-1>", lambda e: go_to_page())
    
    def show_dashboard(self):
        self.create_header()
        
        self.data = self.fetch_data()
        
        overview_label = tk.Label(self.main_area, text="Overview", font=("Arial", 16, "bold"),
                                 bg="#f5f5f5", fg="#333")
        overview_label.pack(anchor=tk.W, padx=40, pady=(10, 10))
        
        cards_frame = tk.Frame(self.main_area, bg="#f5f5f5")
        cards_frame.pack(fill=tk.X, padx=40, pady=10)
        
        cards = [
            ("📦", "Total Products", self.data['total_products'], 100, 50),
            ("📦", "Quantity Sold", self.data['total_sales'], 50, 20),
            ("🛒", "Purchase", f"${self.data['total_purchases']:,.0f}", 10000, 5000),
            ("💰", "Revenue", f"${self.data['total_revenue']:,.0f}", 50000, 20000)
        ]
        
        for icon, label, value, good_threshold, bad_threshold in cards:
            if isinstance(value, str):
                numeric_value = float(value.replace('$', '').replace(',', ''))
                color = self.get_status_color(numeric_value, good_threshold, bad_threshold)
            else:
                color = self.get_status_color(value, good_threshold, bad_threshold)
            
            card = tk.Frame(cards_frame, bg=color, relief=tk.RAISED, bd=2)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
            
            tk.Label(card, text=icon, font=("Arial", 30), bg=color).pack(pady=(15, 5))
            tk.Label(card, text=str(value), font=("Arial", 24, "bold"),
                    bg=color, fg="white").pack()
            tk.Label(card, text=label, font=("Arial", 12),
                    bg=color, fg="white").pack(pady=(5, 15))
        
        self.create_dashboard_charts()
    
    def create_dashboard_charts(self):
        middle_frame = tk.Frame(self.main_area, bg="#f5f5f5")
        middle_frame.pack(fill=tk.BOTH, padx=40, pady=20)
        
        customer_frame = tk.Frame(middle_frame, bg="white", relief=tk.RAISED, bd=1)
        customer_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), ipadx=20, ipady=20)
        
        tk.Label(customer_frame, text="No of Customer", font=("Arial", 14, "bold"),
                bg="white").pack(anchor=tk.W, padx=10, pady=10)
        tk.Label(customer_frame, text="👥", font=("Arial", 40), bg="white").pack(pady=10)
        tk.Label(customer_frame, text=str(self.data['total_customers']),
                font=("Arial", 36, "bold"), bg="white").pack()
        
        inventory_frame = tk.Frame(middle_frame, bg="white", relief=tk.RAISED, bd=1)
        inventory_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, ipadx=20, ipady=20)
        
        tk.Label(inventory_frame, text="Inventory Values", font=("Arial", 14, "bold"),
                bg="white").pack(anchor=tk.W, padx=10, pady=10)
        
        self.create_inventory_chart(inventory_frame)
        
        products_frame = tk.Frame(middle_frame, bg="white", relief=tk.RAISED, bd=1)
        products_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), ipadx=20, ipady=20)
        
        tk.Label(products_frame, text="Top Products by Sales", font=("Arial", 14, "bold"),
                bg="white").pack(anchor=tk.W, padx=10, pady=10)
        
        self.create_top_products_chart(products_frame)
        
        self.create_bottom_section()
    
    def create_inventory_chart(self, parent):
        fig = Figure(figsize=(4, 3), dpi=80)
        ax = fig.add_subplot(111)
        
        available = self.data['available_units']
        sold = self.data['sold_units']
        total = self.data['total_units']
        
        # Only create pie chart if there's data
        if total > 0:
            sizes = [sold, available]
            labels = ['Sold units', 'Available units']
            colors = ['#4c9783', '#b2efdf']  # Updated colors
            
            # Calculate percentages
            sold_percent = (sold / total) * 100 if total > 0 else 0
            available_percent = (available / total) * 100 if total > 0 else 0
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 10})
            ax.axis('equal')
            
            # Add legend with actual numbers
            legend_labels = [
                f'Sold: {sold} ({sold_percent:.1f}%)',
                f'Available: {available} ({available_percent:.1f}%)'
            ]
            ax.legend(legend_labels, loc='upper right', fontsize=8, bbox_to_anchor=(1.2, 1))
        else:
            # Show empty state
            ax.text(0.5, 0.5, 'No Inventory Data', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12, color='gray')
            ax.axis('off')
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_top_products_chart(self, parent):
        canvas_frame = tk.Frame(parent, bg="white")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if not self.data['top_products']:
            tk.Label(canvas_frame, text="No sales data available",
                    bg="white", fg="#666").pack(pady=20)
            return
        
        products = self.data['top_products'][:10]
        names = [p[0] for p in products]
        values = [p[1] for p in products]
        
        fig = Figure(figsize=(4, 4), dpi=80)
        ax = fig.add_subplot(111)
        
        ax.barh(names, values, color='#4c9783')
        ax.set_xlabel('Sales')
        ax.invert_yaxis()
        
        for i, v in enumerate(values):
            ax.text(v, i, f' {v}', va='center', fontsize=8)
        
        canvas = FigureCanvasTkAgg(fig, canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_bottom_section(self):
        bottom_frame = tk.Frame(self.main_area, bg="white", relief=tk.RAISED, bd=1)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        tk.Label(bottom_frame, text="Expenses VS Profit", font=("Arial", 14, "bold"),
                bg="white").pack(anchor=tk.W, padx=20, pady=10)
        
        self.create_line_chart(bottom_frame)
    
    def create_line_chart(self, parent):
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from datetime import datetime
        
        fig = Figure(figsize=(10, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get current year
        current_year = datetime.now().year
        
        # Check if we have financial_data (should always be 12 months now)
        if not self.data.get('financial_data') or len(self.data['financial_data']) == 0:
            # This should rarely happen now
            ax.text(0.5, 0.5, f'No Financial Data for {current_year}\nAdd purchases and sales to see chart', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12, color='gray')
            ax.axis('off')
        else:
            # Extract data - should have all 12 months
            months = [row[0] for row in self.data['financial_data']]
            expenses = [float(row[1]) for row in self.data['financial_data']]
            revenue = [float(row[2]) for row in self.data['financial_data']]
            
            # Check if ALL values are zero
            total_expenses = sum(expenses)
            total_revenue = sum(revenue)
            
            if total_expenses == 0 and total_revenue == 0:
                # All months are zero - show message
                ax.text(0.5, 0.5, f'No Financial Data for {current_year}\nAdd purchases and sales to see chart', 
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       fontsize=12, color='gray')
                ax.axis('off')
            else:
                # Plot expenses line
                line_expenses, = ax.plot(months, expenses, marker='o', linestyle='-', 
                                        color='#ef4444', linewidth=2.5, 
                                        label='Expenses (Purchases)', markersize=8)
                
                # Plot revenue line
                line_revenue, = ax.plot(months, revenue, marker='o', linestyle='-', 
                                       color='#4ade80', linewidth=2.5, 
                                       label='Revenue (Sales)', markersize=8)
                
                # Set y-axis
                y_max = max(max(expenses), max(revenue))
                ax.set_ylim(0, y_max * 1.15)
                
                # Format y-axis to show currency
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                
                # Labels and grid
                ax.set_ylabel('Amount ($)', fontsize=11, fontweight='bold')
                ax.set_xlabel(f'Month ({current_year})', fontsize=11, fontweight='bold')
                ax.set_title(f'Financial Performance - {current_year}', fontsize=12, fontweight='bold', pad=15)
                ax.legend(loc='upper left', fontsize=10)
                ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
                
                # Rotate x-axis labels
                ax.tick_params(axis='x', rotation=0)
                
                # Add value labels on hover
                annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                                  bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.9),
                                  arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                                  fontsize=10, fontweight='bold')
                annot.set_visible(False)
                
                def update_annot(line, ind, line_label):
                    """Update annotation with values"""
                    x, y = line.get_data()
                    pos_x = ind["ind"][0]
                    annot.xy = (x[pos_x], y[pos_x])
                    
                    month = months[pos_x]
                    value = y[pos_x]
                    text = f"{line_label}\n{month}: ${value:,.2f}"
                    
                    annot.set_text(text)
                    annot.get_bbox_patch().set_facecolor('yellow' if 'Expenses' in line_label else 'lightgreen')
                    annot.get_bbox_patch().set_alpha(0.9)
                
                def hover(event):
                    """Show annotation on hover"""
                    vis = annot.get_visible()
                    if event.inaxes == ax:
                        # Check expenses line
                        cont_expenses, ind_expenses = line_expenses.contains(event)
                        if cont_expenses:
                            update_annot(line_expenses, ind_expenses, "Expenses")
                            annot.set_visible(True)
                            fig.canvas.draw_idle()
                            return
                        
                        # Check revenue line
                        cont_revenue, ind_revenue = line_revenue.contains(event)
                        if cont_revenue:
                            update_annot(line_revenue, ind_revenue, "Revenue")
                            annot.set_visible(True)
                            fig.canvas.draw_idle()
                            return
                    
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()
                
                # Connect hover event
                fig.canvas.mpl_connect("motion_notify_event", hover)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def show_sales(self):
        self.create_header()
        
        content_frame = tk.Frame(self.main_area, bg="#f5f5f5")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.data = self.fetch_data()
        
        total_sales_value = self.data['total_sales']
        if total_sales_value >= 50:
            card_color = "#4ade80"
        elif total_sales_value < 20:
            card_color = "#ef4444"
        else:
            card_color = "#fbbf24"
        
        sales_card = tk.Frame(left_frame, bg=card_color, relief=tk.RAISED, bd=2)
        sales_card.pack(anchor=tk.W, padx=20, pady=20)
        
        tk.Label(sales_card, text="📦", font=("Arial", 24), bg=card_color).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(sales_card, text=str(total_sales_value), font=("Arial", 20, "bold"),
                bg=card_color, fg="white").pack(side=tk.LEFT, padx=5)
        tk.Label(sales_card, text="Quantity Sold", font=("Arial", 14),
                bg=card_color, fg="white").pack(side=tk.LEFT, padx=10)
        
        # Add Select and Delete buttons
        action_frame = tk.Frame(left_frame, bg="white")
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.sales_select_btn = tk.Button(action_frame, text="Select", font=("Arial", 11),
                                         bg="#3b82f6", fg="white", width=12, cursor="hand2",
                                         command=self.toggle_sales_selection)
        self.sales_select_btn.pack(side=tk.LEFT, padx=5)
        
        self.sales_delete_btn = tk.Button(action_frame, text="Delete", font=("Arial", 11),
                                         bg="#ef4444", fg="white", width=12, cursor="hand2",
                                         command=self.delete_selected_sales, state=tk.DISABLED)
        self.sales_delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.create_sales_table(left_frame)
        
        # RIGHT FRAME - FIXED WIDTH LIKE INVENTORY
        right_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        tk.Label(right_frame, text="Add Sales Details", font=("Arial", 16, "bold"),
                bg="white").pack(anchor=tk.W, padx=20, pady=20)
        
        self.create_sales_form(right_frame)

    def toggle_sales_selection(self):
        """Toggle between selection mode and normal mode for sales"""
        if not self.sales_selection_mode:
            self.sales_selection_mode = True
            self.sales_select_btn.config(text="Cancel", bg="#6b7280")
            self.sales_delete_btn.config(state=tk.NORMAL)
            
            for item in self.sales_tree.get_children():
                self.sales_tree.item(item, tags=('unchecked',))
            
            self.sales_tree.tag_configure('unchecked', foreground='black')
            self.sales_tree.tag_configure('checked', foreground='blue', font=('Arial', 10, 'bold'))
            
            self.sales_tree.bind('<Button-1>', self.on_sales_checkbox_click)
        else:
            self.sales_selection_mode = False
            self.sales_select_btn.config(text="Select", bg="#3b82f6")
            self.sales_delete_btn.config(state=tk.DISABLED)
            
            for item in self.sales_tree.get_children():
                self.sales_tree.item(item, tags=())
            
            self.sales_checkboxes.clear()
            
            self.sales_tree.unbind('<Button-1>')
            self.sales_tree.bind("<ButtonRelease-1>", self.on_sale_click)
    
    def on_sales_checkbox_click(self, event):
        """Handle checkbox click in sales table"""
        if not self.sales_selection_mode:
            return
        
        region = self.sales_tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.sales_tree.identify_row(event.y)
            if item:
                if item in self.sales_checkboxes:
                    del self.sales_checkboxes[item]
                    self.sales_tree.item(item, tags=('unchecked',))
                else:
                    self.sales_checkboxes[item] = True
                    self.sales_tree.item(item, tags=('checked',))
    
    def delete_selected_sales(self):
        """Delete selected sales items and restore inventory"""
        if not self.sales_checkboxes:
            messagebox.showwarning("Warning", "No items selected")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {len(self.sales_checkboxes)} selected sale(s)?\nInventory will be restored.")
        if not confirm:
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            deleted_count = 0
            restored_items = []
            
            for item_id in self.sales_checkboxes.keys():
                values = self.sales_tree.item(item_id)['values']
                sales_id = values[0]
                product_id = values[1]
                quantity_sold = values[3]
                
                # Check if product exists in inventory
                cur.execute("SELECT product_id, quantity FROM products WHERE product_id = %s", (product_id,))
                product = cur.fetchone()
                
                if product:
                    # Add back quantity to inventory
                    cur.execute("""
                        UPDATE products SET quantity = quantity + %s WHERE product_id = %s
                    """, (quantity_sold, product_id))
                    restored_items.append(f"{product_id}: +{quantity_sold}")
                
                # Delete the sale
                cur.execute("DELETE FROM sales WHERE sales_id = %s", (sales_id,))
                deleted_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            
            restore_msg = "\n".join(restored_items) if restored_items else "No inventory to restore"
            messagebox.showinfo("Success", f"{deleted_count} sale(s) deleted successfully!\n\nInventory Restored:\n{restore_msg}")
            
            self.sales_checkboxes.clear()
            self.toggle_sales_selection()
            self.load_sales_data()
            
            # Refresh dashboard data
            self.data = self.fetch_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete sales: {str(e)}")
            if conn:
                conn.rollback()
                conn.close()
    
    def create_sales_table(self, parent):
        table_frame = tk.Frame(parent, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        y_scroll = tk.Scrollbar(table_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("Sales_ID", "Product_ID", "Employee_ID", "Quantity_Sold", "Total_Amount", "Sales_Date", "User_ID")
        self.sales_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                       yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=120)
        
        y_scroll.config(command=self.sales_tree.yview)
        x_scroll.config(command=self.sales_tree.xview)
        
        self.sales_tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_sales_data()
        
        self.sales_tree.bind("<ButtonRelease-1>", self.on_sale_click)
    
    def load_sales_data(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                
                # Create sales table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sales (
                        sales_id VARCHAR(50) PRIMARY KEY,
                        product_id VARCHAR(50),
                        employee_id VARCHAR(50),
                        quantity_sold INTEGER,
                        total_amount DECIMAL(10, 2),
                        sales_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id VARCHAR(50)
                    )
                """)
                
                # Create users table with user_name
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id VARCHAR(50) PRIMARY KEY,
                        user_name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
                cur.execute("""
                    SELECT sales_id, product_id, employee_id, quantity_sold, total_amount, sales_date, user_id
                    FROM sales ORDER BY sales_date DESC
                """)
                rows = cur.fetchall()
                
                for row in rows:
                    self.sales_tree.insert("", tk.END, values=row)
                
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load sales data: {str(e)}")
                if conn:
                    conn.close()
    
    def create_sales_form(self, parent):
        form_frame = tk.Frame(parent, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        fields = [
            ("Sales_ID*", "sales_id"),
            ("Product_ID* (Select Only)", "product_id"),
            ("Employee_ID* (Select Only)", "employee_id"),
            ("Quantity_Sold*", "quantity_sold"),
            ("Total_Amount", "total_amount"),
            ("Sales_Date", "sales_date"),
            ("User_ID*", "user_id"),
            ("User_Name*", "user_name")
        ]
        
        self.sales_entries = {}
        
        for label, key in fields:
            tk.Label(form_frame, text=label, font=("Arial", 11),
                    bg="white", fg="#333").pack(anchor=tk.W, pady=(10, 2))
            
            if key == "product_id":
                product_container = tk.Frame(form_frame, bg="white")
                product_container.pack(fill=tk.X, pady=(0, 10))
                
                entry = tk.Entry(product_container, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1, state='readonly')
                entry.pack(fill=tk.X)
                self.sales_entries[key] = entry
                
                show_prod_btn = tk.Button(product_container, text="▼ Select Product", 
                                         font=("Arial", 10), bg="#e0e0e0", cursor="hand2",
                                         command=self.show_product_dropdown)
                show_prod_btn.pack(fill=tk.X, pady=(2, 0))
                
                self.product_listbox = tk.Listbox(product_container, height=5, font=("Arial", 10))
                self.product_listbox.pack(fill=tk.X)
                self.product_listbox.pack_forget()
                self.product_listbox.bind("<<ListboxSelect>>", self.on_product_select)
                
            elif key == "employee_id":
                employee_container = tk.Frame(form_frame, bg="white")
                employee_container.pack(fill=tk.X, pady=(0, 10))
                
                entry = tk.Entry(employee_container, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1, state='readonly')
                entry.pack(fill=tk.X)
                self.sales_entries[key] = entry
                
                show_emp_btn = tk.Button(employee_container, text="▼ Select Employee", 
                                        font=("Arial", 10), bg="#e0e0e0", cursor="hand2",
                                        command=self.show_employee_dropdown)
                show_emp_btn.pack(fill=tk.X, pady=(2, 0))
                
                self.employee_listbox = tk.Listbox(employee_container, height=5, font=("Arial", 10))
                self.employee_listbox.pack(fill=tk.X)
                self.employee_listbox.pack_forget()
                self.employee_listbox.bind("<<ListboxSelect>>", self.on_employee_select)
                
            elif key == "user_id":
                user_container = tk.Frame(form_frame, bg="white")
                user_container.pack(fill=tk.X, pady=(0, 10))
                
                entry = tk.Entry(user_container, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1)
                entry.pack(fill=tk.X)
                self.sales_entries[key] = entry
                
                self.user_listbox = tk.Listbox(user_container, height=3, font=("Arial", 10))
                self.user_listbox.pack(fill=tk.X)
                self.user_listbox.pack_forget()
                
                entry.bind("<KeyRelease>", self.on_user_change)
                self.user_listbox.bind("<<ListboxSelect>>", self.on_user_select)
                
            else:
                entry = tk.Entry(form_frame, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1)
                entry.pack(fill=tk.X, pady=(0, 10))
                self.sales_entries[key] = entry
                
                if key == "sales_id":
                    entry.bind("<KeyRelease>", self.on_sales_id_change)
        
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Clear", font=("Arial", 12),
                 bg="white", fg="#333", width=12, cursor="hand2",
                 relief=tk.SOLID, bd=1, command=self.clear_sales_form).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Add Sale", font=("Arial", 12),
                 bg="#4b9783", fg="white", width=12, cursor="hand2",
                 bd=0, command=self.add_sale).pack(side=tk.LEFT, padx=10)
    
    def show_product_dropdown(self):
        """Show all available products in dropdown"""
        if self.product_listbox.winfo_ismapped():
            self.product_listbox.pack_forget()
        else:
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT product_id FROM products ORDER BY product_id")
                    products = [row[0] for row in cur.fetchall()]
                    cur.close()
                    conn.close()
                    
                    self.product_listbox.delete(0, tk.END)
                    for prod in products:
                        self.product_listbox.insert(tk.END, prod)
                    self.product_listbox.pack(fill=tk.X)
                except:
                    if conn:
                        conn.close()
    
    def show_employee_dropdown(self):
        """Show all available employees in dropdown"""
        if self.employee_listbox.winfo_ismapped():
            self.employee_listbox.pack_forget()
        else:
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT employee_id FROM employees ORDER BY employee_id")
                    employees = [row[0] for row in cur.fetchall()]
                    cur.close()
                    conn.close()
                    
                    self.employee_listbox.delete(0, tk.END)
                    for emp in employees:
                        self.employee_listbox.insert(tk.END, emp)
                    self.employee_listbox.pack(fill=tk.X)
                except:
                    if conn:
                        conn.close()
    
    def on_product_select(self, event):
        selection = self.product_listbox.curselection()
        if selection:
            product = self.product_listbox.get(selection[0])
            self.sales_entries['product_id'].config(state='normal')
            self.sales_entries['product_id'].delete(0, tk.END)
            self.sales_entries['product_id'].insert(0, product)
            self.sales_entries['product_id'].config(state='readonly')
            self.product_listbox.pack_forget()
    
    def on_employee_select(self, event):
        selection = self.employee_listbox.curselection()
        if selection:
            employee = self.employee_listbox.get(selection[0])
            self.sales_entries['employee_id'].config(state='normal')
            self.sales_entries['employee_id'].delete(0, tk.END)
            self.sales_entries['employee_id'].insert(0, employee)
            self.sales_entries['employee_id'].config(state='readonly')
            self.employee_listbox.pack_forget()
    
    def on_user_change(self, event):
        typed = self.sales_entries['user_id'].get().lower()
        
        if not typed:
            self.user_listbox.pack_forget()
            return
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT user_id FROM users WHERE user_id IS NOT NULL")
                users = [row[0] for row in cur.fetchall()]
                cur.close()
                conn.close()
                
                matching = [user for user in users if typed in user.lower()]
                
                if matching:
                    self.user_listbox.delete(0, tk.END)
                    for user in matching[:5]:
                        self.user_listbox.insert(tk.END, user)
                    self.user_listbox.pack(fill=tk.X)
                else:
                    self.user_listbox.pack_forget()
            except:
                if conn:
                    conn.close()
    
    def on_user_select(self, event):
        selection = self.user_listbox.curselection()
        if selection:
            user_id = self.user_listbox.get(selection[0])
            self.sales_entries['user_id'].delete(0, tk.END)
            self.sales_entries['user_id'].insert(0, user_id)
            self.user_listbox.pack_forget()
            
            # Auto-fill user_name when user_id is selected
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT user_name FROM users WHERE user_id = %s", (user_id,))
                    result = cur.fetchone()
                    if result:
                        self.sales_entries['user_name'].delete(0, tk.END)
                        self.sales_entries['user_name'].insert(0, result[0])
                    cur.close()
                    conn.close()
                except:
                    if conn:
                        conn.close()
    
    def on_sales_id_change(self, event):
        sales_id = self.sales_entries['sales_id'].get()
        if sales_id:
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT product_id, employee_id, quantity_sold, total_amount, sales_date, user_id
                        FROM sales WHERE sales_id = %s
                    """, (sales_id,))
                    result = cur.fetchone()
                    
                    if result:
                        # Fill all fields as readonly except quantity_sold
                        self.sales_entries['product_id'].config(state='normal')
                        self.sales_entries['product_id'].delete(0, tk.END)
                        self.sales_entries['product_id'].insert(0, result[0])
                        self.sales_entries['product_id'].config(state='readonly')
                        
                        self.sales_entries['employee_id'].config(state='normal')
                        self.sales_entries['employee_id'].delete(0, tk.END)
                        self.sales_entries['employee_id'].insert(0, result[1])
                        self.sales_entries['employee_id'].config(state='readonly')
                        
                        self.sales_entries['quantity_sold'].delete(0, tk.END)
                        self.sales_entries['quantity_sold'].config(state='normal')
                        
                        self.sales_entries['total_amount'].delete(0, tk.END)
                        self.sales_entries['total_amount'].insert(0, result[3])
                        self.sales_entries['total_amount'].config(state='readonly')
                        
                        self.sales_entries['sales_date'].delete(0, tk.END)
                        self.sales_entries['sales_date'].insert(0, result[4])
                        self.sales_entries['sales_date'].config(state='readonly')
                        
                        self.sales_entries['user_id'].delete(0, tk.END)
                        self.sales_entries['user_id'].insert(0, result[5])
                        self.sales_entries['user_id'].config(state='readonly')
                        
                        # Get user_name
                        cur.execute("SELECT user_name FROM users WHERE user_id = %s", (result[5],))
                        user_result = cur.fetchone()
                        if user_result:
                            self.sales_entries['user_name'].delete(0, tk.END)
                            self.sales_entries['user_name'].insert(0, user_result[0])
                            self.sales_entries['user_name'].config(state='readonly')
                    else:
                        # Enable all fields for new entry
                        for key in ['product_id', 'employee_id', 'total_amount', 'sales_date', 'user_id', 'user_name']:
                            if key in ['product_id', 'employee_id']:
                                self.sales_entries[key].config(state='readonly')
                            else:
                                self.sales_entries[key].config(state='normal')
                    
                    cur.close()
                    conn.close()
                except Exception as e:
                    if conn:
                        conn.close()
    
    def on_sale_click(self, event):
        selection = self.sales_tree.selection()
        if selection:
            item = self.sales_tree.item(selection[0])
            values = item['values']
            
            self.clear_sales_form()
            
            keys = ['sales_id', 'product_id', 'employee_id', 'quantity_sold', 'total_amount', 'sales_date', 'user_id']
            for i, key in enumerate(keys):
                if key in ['product_id', 'employee_id']:
                    self.sales_entries[key].config(state='normal')
                self.sales_entries[key].insert(0, str(values[i]))
                if key in ['product_id', 'employee_id']:
                    self.sales_entries[key].config(state='readonly')
    
    def clear_sales_form(self):
        for key, entry in self.sales_entries.items():
            if key in ['product_id', 'employee_id']:
                entry.config(state='normal')
            entry.delete(0, tk.END)
            if key in ['product_id', 'employee_id']:
                entry.config(state='readonly')
    
    def add_sale(self):
        sales_id = self.sales_entries['sales_id'].get().strip()
        product_id = self.sales_entries['product_id'].get().strip()
        employee_id = self.sales_entries['employee_id'].get().strip()
        quantity_sold = self.sales_entries['quantity_sold'].get().strip()
        total_amount = self.sales_entries['total_amount'].get().strip()
        user_id = self.sales_entries['user_id'].get().strip()
        user_name = self.sales_entries['user_name'].get().strip()
        sales_date = self.sales_entries['sales_date'].get().strip()

        if not sales_id or not product_id or not employee_id or not quantity_sold or not user_id or not user_name:
            messagebox.showerror("Error", "Sales ID, Product ID, Employee ID, Quantity Sold, User ID, and User Name are required")
            return
        
        try:
            quantity_sold = int(quantity_sold)
            if quantity_sold <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return
        
        try:
            total_amount = float(total_amount) if total_amount else 0
        except ValueError:
            messagebox.showerror("Error", "Total amount must be a number")
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            
            # STEP 1: Verify product exists FIRST
            cur.execute("SELECT product_id, price, quantity FROM products WHERE product_id = %s", (product_id,))
            product = cur.fetchone()
            if not product:
                messagebox.showerror("Error", f"Product ID '{product_id}' does not exist. Please select from existing products.")
                cur.close()
                conn.close()
                return
            
            # Check if enough quantity available
            available_quantity = product[2] or 0
            
            # STEP 2: Verify employee exists
            cur.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (employee_id,))
            if not cur.fetchone():
                messagebox.showerror("Error", f"Employee ID '{employee_id}' does not exist. Please select from existing employees.")
                cur.close()
                conn.close()
                return
            
            # STEP 3: Calculate total amount if not provided
            if not total_amount:
                total_amount = product[1] * quantity_sold
            
            # STEP 4: Handle sales_date - use custom date or default to now
            if sales_date and sales_date != "YYYY-MM-DD (optional)":
                try:
                    from datetime import datetime
                    if len(sales_date) == 10:
                        datetime.strptime(sales_date, '%Y-%m-%d')
                        sales_date_value = sales_date + ' 00:00:00'
                    else:
                        datetime.strptime(sales_date, '%Y-%m-%d %H:%M:%S')
                        sales_date_value = sales_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format!\nUse: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS\nExample: 2025-10-21 or 2025-10-21 14:30:00")
                    cur.close()
                    conn.close()
                    return
            else:
                sales_date_value = None
            
            # STEP 5: Check if sales_id exists (for updates)
            cur.execute("SELECT sales_id, quantity_sold, product_id FROM sales WHERE sales_id = %s", (sales_id,))
            existing_sale = cur.fetchone()
            
            if existing_sale:
                # UPDATE EXISTING SALE
                old_quantity = existing_sale[1]
                old_product_id = existing_sale[2]
                
                # If product changed or quantity changed, adjust inventory
                if old_product_id == product_id:
                    # Same product, adjust the difference
                    quantity_difference = quantity_sold - old_quantity
                    
                    if quantity_difference > 0:
                        # Selling more - check if enough stock
                        if available_quantity < quantity_difference:
                            messagebox.showerror("Error", f"Insufficient stock! Available: {available_quantity}, Trying to sell: {quantity_difference} more")
                            cur.close()
                            conn.close()
                            return
                        
                        # Subtract additional quantity
                        cur.execute("""
                            UPDATE products SET quantity = quantity - %s WHERE product_id = %s
                        """, (quantity_difference, product_id))
                    elif quantity_difference < 0:
                        # Selling less - add back the difference
                        cur.execute("""
                            UPDATE products SET quantity = quantity + %s WHERE product_id = %s
                        """, (abs(quantity_difference), product_id))
                
                # Update sale with or without date
                if sales_date_value:
                    cur.execute("""
                        UPDATE sales SET quantity_sold = %s, total_amount = %s, product_id = %s, sales_date = %s
                        WHERE sales_id = %s
                    """, (quantity_sold, total_amount, product_id, sales_date_value, sales_id))
                else:
                    cur.execute("""
                        UPDATE sales SET quantity_sold = %s, total_amount = %s, product_id = %s
                        WHERE sales_id = %s
                    """, (quantity_sold, total_amount, product_id, sales_id))
                
                messagebox.showinfo("Success", "Sale updated successfully!\nInventory adjusted.")
            else:
                # NEW SALE - check stock availability
                if available_quantity < quantity_sold:
                    messagebox.showerror("Error", f"Insufficient stock! Available: {available_quantity}, Trying to sell: {quantity_sold}")
                    cur.close()
                    conn.close()
                    return
                
                # Create or update user with user_name
                cur.execute("""
                    INSERT INTO users (user_id, user_name) VALUES (%s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET user_name = EXCLUDED.user_name
                """, (user_id, user_name))
                
                # Insert new sale with or without custom date
                if sales_date_value:
                    cur.execute("""
                        INSERT INTO sales (sales_id, product_id, employee_id, quantity_sold, total_amount, user_id, sales_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (sales_id, product_id, employee_id, quantity_sold, total_amount, user_id, sales_date_value))
                else:
                    cur.execute("""
                        INSERT INTO sales (sales_id, product_id, employee_id, quantity_sold, total_amount, user_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (sales_id, product_id, employee_id, quantity_sold, total_amount, user_id))
                
                # SUBTRACT FROM INVENTORY - THIS IS THE KEY LINE
                cur.execute("""
                    UPDATE products SET quantity = quantity - %s WHERE product_id = %s
                """, (quantity_sold, product_id))
                
                messagebox.showinfo("Success", f"Sale added successfully!\nInventory updated: {available_quantity} → {available_quantity - quantity_sold}")
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.clear_sales_form()
            self.load_sales_data()
            
            # Refresh dashboard data
            self.data = self.fetch_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add sale: {str(e)}")
            if conn:
                conn.rollback()
                conn.close()  

    def show_purchase(self):
        self.create_header()
        
        content_frame = tk.Frame(self.main_area, bg="#f5f5f5")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.data = self.fetch_data()
        
        total_purchase_value = self.data['total_purchases']
        if total_purchase_value >= 10000:
            card_color = "#4ade80"
        elif total_purchase_value < 5000:
            card_color = "#ef4444"
        else:
            card_color = "#fbbf24"
        
        purchase_card = tk.Frame(left_frame, bg=card_color, relief=tk.RAISED, bd=2)
        purchase_card.pack(anchor=tk.W, padx=20, pady=20)
        
        tk.Label(purchase_card, text="🛒", font=("Arial", 24), bg=card_color).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(purchase_card, text=f"${total_purchase_value:,.0f}", font=("Arial", 20, "bold"),
                bg=card_color, fg="white").pack(side=tk.LEFT, padx=5)
        tk.Label(purchase_card, text="Total Purchase", font=("Arial", 14),
                bg=card_color, fg="white").pack(side=tk.LEFT, padx=10)
        
        # Add Select and Delete buttons
        action_frame = tk.Frame(left_frame, bg="white")
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.purchase_select_btn = tk.Button(action_frame, text="Select", font=("Arial", 11),
                                            bg="#3b82f6", fg="white", width=12, cursor="hand2",
                                            command=self.toggle_purchase_selection)
        self.purchase_select_btn.pack(side=tk.LEFT, padx=5)
        
        self.purchase_delete_btn = tk.Button(action_frame, text="Delete", font=("Arial", 11),
                                            bg="#ef4444", fg="white", width=12, cursor="hand2",
                                            command=self.delete_selected_purchases, state=tk.DISABLED)
        self.purchase_delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.create_purchase_table(left_frame)
        
        # RIGHT FRAME - FIXED WIDTH LIKE INVENTORY
        right_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        tk.Label(right_frame, text="Add Purchase Details", font=("Arial", 16, "bold"),
                bg="white").pack(anchor=tk.W, padx=20, pady=20)
        
        self.create_purchase_form(right_frame)
    
    def toggle_purchase_selection(self):
        """Toggle between selection mode and normal mode for purchases"""
        if not self.purchase_selection_mode:
            self.purchase_selection_mode = True
            self.purchase_select_btn.config(text="Cancel", bg="#6b7280")
            self.purchase_delete_btn.config(state=tk.NORMAL)
            
            for item in self.purchase_tree.get_children():
                self.purchase_tree.item(item, tags=('unchecked',))
            
            self.purchase_tree.tag_configure('unchecked', foreground='black')
            self.purchase_tree.tag_configure('checked', foreground='blue', font=('Arial', 10, 'bold'))
            
            self.purchase_tree.bind('<Button-1>', self.on_purchase_checkbox_click)
        else:
            self.purchase_selection_mode = False
            self.purchase_select_btn.config(text="Select", bg="#3b82f6")
            self.purchase_delete_btn.config(state=tk.DISABLED)
            
            for item in self.purchase_tree.get_children():
                self.purchase_tree.item(item, tags=())
            
            self.purchase_checkboxes.clear()
            
            self.purchase_tree.unbind('<Button-1>')
            self.purchase_tree.bind("<ButtonRelease-1>", self.on_purchase_click)
    
    def on_purchase_checkbox_click(self, event):
        """Handle checkbox click in purchase table"""
        if not self.purchase_selection_mode:
            return
        
        region = self.purchase_tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.purchase_tree.identify_row(event.y)
            if item:
                if item in self.purchase_checkboxes:
                    del self.purchase_checkboxes[item]
                    self.purchase_tree.item(item, tags=('unchecked',))
                else:
                    self.purchase_checkboxes[item] = True
                    self.purchase_tree.item(item, tags=('checked',))
    
    def delete_selected_purchases(self):
        """Delete selected purchase items"""
        if not self.purchase_checkboxes:
            messagebox.showwarning("Warning", "No items selected")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {len(self.purchase_checkboxes)} selected purchase(s)?")
        if not confirm:
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            deleted_count = 0
            
            for item_id in self.purchase_checkboxes.keys():
                values = self.purchase_tree.item(item_id)['values']
                purchase_id = values[0]
                
                cur.execute("DELETE FROM purchases WHERE purchase_id = %s", (purchase_id,))
                deleted_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            
            messagebox.showinfo("Success", f"{deleted_count} purchase(s) deleted successfully!")
            
            self.purchase_checkboxes.clear()
            self.toggle_purchase_selection()
            self.load_purchase_data()
            
            self.data = self.fetch_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete purchases: {str(e)}")
            if conn:
                conn.close()
    
    def create_purchase_table(self, parent):
        table_frame = tk.Frame(parent, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        y_scroll = tk.Scrollbar(table_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("Purchase_ID", "Product_ID", "Quantity_Purchased", "Total_Cost", "Purchase_Date", "Supplier")
        self.purchase_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        for col in columns:
            self.purchase_tree.heading(col, text=col)
            self.purchase_tree.column(col, width=140)
        
        y_scroll.config(command=self.purchase_tree.yview)
        x_scroll.config(command=self.purchase_tree.xview)
        
        self.purchase_tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_purchase_data()
        
        self.purchase_tree.bind("<ButtonRelease-1>", self.on_purchase_click)
    
    def load_purchase_data(self):
        for item in self.purchase_tree.get_children():
            self.purchase_tree.delete(item)
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                
                # Create purchases table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS purchases (
                        purchase_id VARCHAR(50) PRIMARY KEY,
                        product_id VARCHAR(50),
                        quantity_purchased INTEGER,
                        total_cost DECIMAL(10, 2),
                        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        supplier VARCHAR(100)
                    )
                """)
                
                conn.commit()
                
                cur.execute("""
                    SELECT purchase_id, product_id, quantity_purchased, total_cost, purchase_date, supplier
                    FROM purchases ORDER BY purchase_date DESC
                """)
                rows = cur.fetchall()
                
                for row in rows:
                    self.purchase_tree.insert("", tk.END, values=row)
                
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load purchase data: {str(e)}")
                if conn:
                    conn.close()
    
    def create_purchase_form(self, parent):
        form_frame = tk.Frame(parent, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        fields = [
            ("Purchase_ID*", "purchase_id"),
            ("Product_ID*", "product_id"),
            ("Quantity_Purchased*", "quantity_purchased"),
            ("Total_Cost", "total_cost"),
            ("Purchase_Date", "purchase_date"),
            ("Supplier", "supplier")
        ]
        
        self.purchase_entries = {}
        
        for label, key in fields:
            tk.Label(form_frame, text=label, font=("Arial", 11),
                    bg="white", fg="#333").pack(anchor=tk.W, pady=(10, 2))
            
            if key == "product_id":
                product_container = tk.Frame(form_frame, bg="white")
                product_container.pack(fill=tk.X, pady=(0, 10))
                
                entry = tk.Entry(product_container, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1)
                entry.pack(fill=tk.X)
                self.purchase_entries[key] = entry
                
                self.purchase_product_listbox = tk.Listbox(product_container, height=3, font=("Arial", 10))
                self.purchase_product_listbox.pack(fill=tk.X)
                self.purchase_product_listbox.pack_forget()
                
                entry.bind("<KeyRelease>", self.on_purchase_product_change)
                self.purchase_product_listbox.bind("<<ListboxSelect>>", self.on_purchase_product_select)
                
            elif key == "supplier":
                supplier_container = tk.Frame(form_frame, bg="white")
                supplier_container.pack(fill=tk.X, pady=(0, 10))
                
                entry = tk.Entry(supplier_container, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1)
                entry.pack(fill=tk.X)
                self.purchase_entries[key] = entry
                
                self.purchase_supplier_listbox = tk.Listbox(supplier_container, height=3, font=("Arial", 10))
                self.purchase_supplier_listbox.pack(fill=tk.X)
                self.purchase_supplier_listbox.pack_forget()
                
                entry.bind("<KeyRelease>", self.on_purchase_supplier_change)
                self.purchase_supplier_listbox.bind("<<ListboxSelect>>", self.on_purchase_supplier_select)
                
            else:
                entry = tk.Entry(form_frame, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1)
                entry.pack(fill=tk.X, pady=(0, 10))
                self.purchase_entries[key] = entry
                
                if key == "purchase_id":
                    entry.bind("<KeyRelease>", self.on_purchase_id_change)
        
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Clear", font=("Arial", 12),
                 bg="white", fg="#333", width=12, cursor="hand2",
                 relief=tk.SOLID, bd=1, command=self.clear_purchase_form).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Add Purchase", font=("Arial", 12),
                 bg="#4b9783", fg="white", width=12, cursor="hand2",
                 bd=0, command=self.add_purchase).pack(side=tk.LEFT, padx=10)
   
    def on_purchase_product_change(self, event):
        typed = self.purchase_entries['product_id'].get().lower()
        
        if not typed:
            self.purchase_product_listbox.pack_forget()
            return
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT product_id FROM products WHERE product_id IS NOT NULL")
                products = [row[0] for row in cur.fetchall()]
                cur.close()
                conn.close()
                
                matching = [prod for prod in products if typed in prod.lower()]
                
                if matching:
                    self.purchase_product_listbox.delete(0, tk.END)
                    for prod in matching[:5]:
                        self.purchase_product_listbox.insert(tk.END, prod)
                    self.purchase_product_listbox.pack(fill=tk.X)
                else:
                    self.purchase_product_listbox.pack_forget()
            except:
                if conn:
                    conn.close()
    
    def on_purchase_product_select(self, event):
        selection = self.purchase_product_listbox.curselection()
        if selection:
            product_id = self.purchase_product_listbox.get(selection[0])
            self.purchase_entries['product_id'].delete(0, tk.END)
            self.purchase_entries['product_id'].insert(0, product_id)
            self.purchase_product_listbox.pack_forget()
    
    def on_purchase_supplier_change(self, event):
        typed = self.purchase_entries['supplier'].get().lower()
        
        if not typed:
            self.purchase_supplier_listbox.pack_forget()
            return
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT supplier FROM purchases WHERE supplier IS NOT NULL")
                suppliers = [row[0] for row in cur.fetchall()]
                cur.close()
                conn.close()
                
                matching = [sup for sup in suppliers if typed in sup.lower()]
                
                if matching:
                    self.purchase_supplier_listbox.delete(0, tk.END)
                    for sup in matching[:5]:
                        self.purchase_supplier_listbox.insert(tk.END, sup)
                    self.purchase_supplier_listbox.pack(fill=tk.X)
                else:
                    self.purchase_supplier_listbox.pack_forget()
            except:
                if conn:
                    conn.close()
    
    def on_purchase_supplier_select(self, event):
        selection = self.purchase_supplier_listbox.curselection()
        if selection:
            supplier = self.purchase_supplier_listbox.get(selection[0])
            self.purchase_entries['supplier'].delete(0, tk.END)
            self.purchase_entries['supplier'].insert(0, supplier)
            self.purchase_supplier_listbox.pack_forget()
    
    def on_purchase_id_change(self, event):
        purchase_id = self.purchase_entries['purchase_id'].get()
        if purchase_id:
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT product_id, quantity_purchased, total_cost, purchase_date, supplier
                        FROM purchases WHERE purchase_id = %s
                    """, (purchase_id,))
                    result = cur.fetchone()
                    
                    if result:
                        # Fill all fields as readonly except quantity_purchased
                        self.purchase_entries['product_id'].delete(0, tk.END)
                        self.purchase_entries['product_id'].insert(0, result[0])
                        self.purchase_entries['product_id'].config(state='readonly')
                        
                        self.purchase_entries['quantity_purchased'].delete(0, tk.END)
                        self.purchase_entries['quantity_purchased'].config(state='normal')
                        
                        self.purchase_entries['total_cost'].delete(0, tk.END)
                        self.purchase_entries['total_cost'].insert(0, result[2])
                        self.purchase_entries['total_cost'].config(state='readonly')
                        
                        self.purchase_entries['purchase_date'].delete(0, tk.END)
                        self.purchase_entries['purchase_date'].insert(0, result[3])
                        self.purchase_entries['purchase_date'].config(state='readonly')
                        
                        self.purchase_entries['supplier'].delete(0, tk.END)
                        self.purchase_entries['supplier'].insert(0, result[4])
                        self.purchase_entries['supplier'].config(state='readonly')
                    else:
                        # Enable all fields for new entry
                        for key in ['product_id', 'total_cost', 'purchase_date', 'supplier']:
                            self.purchase_entries[key].config(state='normal')
                    
                    cur.close()
                    conn.close()
                except Exception as e:
                    if conn:
                        conn.close()
    
    def on_purchase_click(self, event):
        selection = self.purchase_tree.selection()
        if selection:
            item = self.purchase_tree.item(selection[0])
            values = item['values']
            
            self.clear_purchase_form()
            
            keys = ['purchase_id', 'product_id', 'quantity_purchased', 'total_cost', 'purchase_date', 'supplier']
            for i, key in enumerate(keys):
                self.purchase_entries[key].insert(0, str(values[i]))
    
    def clear_purchase_form(self):
        for entry in self.purchase_entries.values():
            entry.config(state='normal')
            entry.delete(0, tk.END)
    
    def add_purchase(self):
        purchase_id = self.purchase_entries['purchase_id'].get().strip()
        product_id = self.purchase_entries['product_id'].get().strip()
        quantity_purchased = self.purchase_entries['quantity_purchased'].get().strip()
        total_cost = self.purchase_entries['total_cost'].get().strip()
        supplier = self.purchase_entries['supplier'].get().strip()
        purchase_date = self.purchase_entries['purchase_date'].get().strip()
        
        if not purchase_id or not product_id or not quantity_purchased:
            messagebox.showerror("Error", "Purchase ID, Product ID, and Quantity Purchased are required")
            return
        
        try:
            quantity_purchased = int(quantity_purchased)
            if quantity_purchased <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return
        
        try:
            total_cost = float(total_cost) if total_cost else 0
            if total_cost < 0:
                messagebox.showerror("Error", "Total cost cannot be negative")
                return
        except ValueError:
            messagebox.showerror("Error", "Total cost must be a number")
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            
            # Handle purchase_date
            if purchase_date and purchase_date != "YYYY-MM-DD (optional)":
                try:
                    from datetime import datetime
                    if len(purchase_date) == 10:
                        datetime.strptime(purchase_date, '%Y-%m-%d')
                        purchase_date_value = purchase_date + ' 00:00:00'
                    else:
                        datetime.strptime(purchase_date, '%Y-%m-%d %H:%M:%S')
                        purchase_date_value = purchase_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format!\nUse: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS")
                    cur.close()
                    conn.close()
                    return
            else:
                purchase_date_value = None
            
            # STEP 1: Check if product exists in inventory
            cur.execute("SELECT product_id, price, quantity FROM products WHERE product_id = %s", (product_id,))
            product = cur.fetchone()
            
            if not product:
                # Product doesn't exist - ask user if they want to create it
                response = messagebox.askyesno(
                    "Product Not Found",
                    f"Product '{product_id}' does not exist in inventory.\n\n"
                    f"Do you want to create this product?\n\n"
                    f"It will be added to inventory with:\n"
                    f"- Quantity: {quantity_purchased}\n"
                    f"- Supplier: {supplier}"
                )
                
                if not response:
                    cur.close()
                    conn.close()
                    return
                
                # Calculate price per unit
                price_per_unit = total_cost / quantity_purchased if total_cost and quantity_purchased else 0
                
                # Create new product in inventory
                cur.execute("""
                    INSERT INTO products (product_id, product_name, category, quantity, price, supplier)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (product_id, product_id, 'Purchased', quantity_purchased, price_per_unit, supplier))
                
                messagebox.showinfo("Product Created", f"Product '{product_id}' created in inventory with quantity: {quantity_purchased}")
            else:
                # Product exists - will update inventory after purchase is added
                existing_quantity = product[2] or 0
            
            # STEP 2: Check if purchase_id exists
            cur.execute("SELECT purchase_id, quantity_purchased, product_id FROM purchases WHERE purchase_id = %s", (purchase_id,))
            existing_purchase = cur.fetchone()
            
            if existing_purchase:
                # UPDATE EXISTING PURCHASE
                old_quantity = existing_purchase[1]
                old_product_id = existing_purchase[2]
                
                # Calculate quantity difference
                quantity_difference = quantity_purchased - old_quantity
                
                # Update purchase record
                if purchase_date_value:
                    cur.execute("""
                        UPDATE purchases 
                        SET quantity_purchased = %s, total_cost = %s, product_id = %s, 
                            supplier = %s, purchase_date = %s
                        WHERE purchase_id = %s
                    """, (quantity_purchased, total_cost, product_id, supplier, purchase_date_value, purchase_id))
                else:
                    cur.execute("""
                        UPDATE purchases 
                        SET quantity_purchased = %s, total_cost = %s, product_id = %s, supplier = %s
                        WHERE purchase_id = %s
                    """, (quantity_purchased, total_cost, product_id, supplier, purchase_id))
                
                # Update inventory based on quantity difference
                if old_product_id == product_id:
                    # Same product - adjust by difference
                    if quantity_difference != 0:
                        cur.execute("""
                            UPDATE products SET quantity = quantity + %s WHERE product_id = %s
                        """, (quantity_difference, product_id))
                        
                        if quantity_difference > 0:
                            msg = f"Purchase updated!\nAdded {quantity_difference} more units to inventory."
                        else:
                            msg = f"Purchase updated!\nRemoved {abs(quantity_difference)} units from inventory."
                        messagebox.showinfo("Success", msg)
                    else:
                        messagebox.showinfo("Success", "Purchase updated successfully!")
                else:
                    # Product changed - remove from old, add to new
                    cur.execute("""
                        UPDATE products SET quantity = quantity - %s WHERE product_id = %s
                    """, (old_quantity, old_product_id))
                    
                    cur.execute("""
                        UPDATE products SET quantity = quantity + %s WHERE product_id = %s
                    """, (quantity_purchased, product_id))
                    
                    messagebox.showinfo("Success", "Purchase updated!\nInventory adjusted for both products.")
                
            else:
                # NEW PURCHASE - Insert and update inventory
                if purchase_date_value:
                    cur.execute("""
                        INSERT INTO purchases (purchase_id, product_id, quantity_purchased, total_cost, supplier, purchase_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (purchase_id, product_id, quantity_purchased, total_cost, supplier, purchase_date_value))
                else:
                    cur.execute("""
                        INSERT INTO purchases (purchase_id, product_id, quantity_purchased, total_cost, supplier)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (purchase_id, product_id, quantity_purchased, total_cost, supplier))
                
                # Update inventory quantity if product already existed
                if product:
                    cur.execute("""
                        UPDATE products SET quantity = quantity + %s WHERE product_id = %s
                    """, (quantity_purchased, product_id))
                    
                    new_quantity = existing_quantity + quantity_purchased
                    messagebox.showinfo("Success", f"Purchase added successfully!\n\nInventory updated:\n{product_id}: {existing_quantity} → {new_quantity} (+{quantity_purchased})")
                else:
                    # Product was just created
                    messagebox.showinfo("Success", f"Purchase added successfully!\nNew product added to inventory.")
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.clear_purchase_form()
            self.load_purchase_data()
            
            # Refresh dashboard data
            self.data = self.fetch_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add purchase: {str(e)}")
            if conn:
                conn.rollback()
                conn.close()
                
    def show_contact(self):
        """Contact Us page for submitting issues to admin"""
        self.create_header()
        
        # Main container - USE PACK INSTEAD OF PLACE
        contact_container = tk.Frame(self.main_area, bg="white", relief=tk.RAISED, bd=2)
        contact_container.pack(pady=50, padx=200, fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(contact_container, text="Contact Us", font=("Arial", 24, "bold"),
                bg="white", fg="#333").pack(pady=(30, 20))
        
        # Form frame
        form_frame = tk.Frame(contact_container, bg="white")
        form_frame.pack(padx=50, fill=tk.BOTH, expand=True)
        
        # Email ID
        tk.Label(form_frame, text="Email ID", font=("Arial", 12),
                bg="white", fg="#333", anchor="w").pack(fill=tk.X, pady=(0, 5))
        
        email_entry = tk.Entry(form_frame, font=("Arial", 12), bg="white",
                              relief=tk.SOLID, bd=1)
        email_entry.pack(fill=tk.X, ipady=8, pady=(0, 20))
        
        # Issue description
        tk.Label(form_frame, text="Please Tell us the issue", font=("Arial", 12),
                bg="white", fg="#333", anchor="w").pack(fill=tk.X, pady=(0, 5))
        
        issue_text = tk.Text(form_frame, font=("Arial", 11), bg="white",
                            relief=tk.SOLID, bd=1, height=8, wrap=tk.WORD)
        issue_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(pady=20, fill=tk.X)
        
        def clear_form():
            """Clear all form fields"""
            email_entry.delete(0, tk.END)
            issue_text.delete('1.0', tk.END)
        
        def submit_issue():
            """Submit issue to admin"""
            email = email_entry.get().strip()
            issue = issue_text.get('1.0', tk.END).strip()
            
            if not email:
                messagebox.showerror("Error", "Please enter your email ID")
                return
            
            if not issue:
                messagebox.showerror("Error", "Please describe the issue")
                return
            
            # Validate email format (basic)
            if '@' not in email or '.' not in email:
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            
            conn = self.get_db_connection()
            if not conn:
                return
            
            try:
                cur = conn.cursor()
                
                # Create contact_issues table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS contact_issues (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(100),
                        issue TEXT,
                        submitted_by VARCHAR(50),
                        status VARCHAR(20) DEFAULT 'Pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        read BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Insert issue
                cur.execute("""
                    INSERT INTO contact_issues (email, issue, submitted_by)
                    VALUES (%s, %s, %s)
                """, (email, issue, self.username))
                
                conn.commit()
                cur.close()
                conn.close()
                
                messagebox.showinfo("Success", "Your issue has been submitted successfully!\nAdmin will be notified.")
                clear_form()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to submit issue: {str(e)}")
                if conn:
                    conn.rollback()
                    conn.close()
        
        # Submit button (right side)
        submit_btn = tk.Button(btn_frame, text="Submit", font=("Arial", 12),
                              bg="#4b9783", fg="white", width=12, height=2,
                              bd=0, cursor="hand2",
                              command=submit_issue)
        submit_btn.pack(side=tk.RIGHT)
        
        # Clear button (right side, before submit)
        clear_btn = tk.Button(btn_frame, text="Clear", font=("Arial", 12),
                             bg="white", fg="#333", width=12, height=2,
                             relief=tk.SOLID, bd=1, cursor="hand2",
                             command=clear_form)
        clear_btn.pack(side=tk.RIGHT, padx=(0, 10))

    
    # Continuing with inventory and other methods...
    def show_inventory(self):
        self.create_header()
        
        content_frame = tk.Frame(self.main_area, bg="#f5f5f5")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.data = self.fetch_data()
        
        total_products_value = self.data['total_products']
        if total_products_value >= 100:
            card_color = "#4ade80"
        elif total_products_value < 50:
            card_color = "#ef4444"
        else:
            card_color = "#fbbf24"
        
        product_card = tk.Frame(left_frame, bg=card_color, relief=tk.RAISED, bd=2)
        product_card.pack(anchor=tk.W, padx=20, pady=20)
        
        tk.Label(product_card, text="📦", font=("Arial", 24), bg=card_color).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(product_card, text=str(total_products_value), font=("Arial", 20, "bold"),
                bg=card_color, fg="white").pack(side=tk.LEFT, padx=5)
        tk.Label(product_card, text="Total Products", font=("Arial", 14),
                bg=card_color, fg="white").pack(side=tk.LEFT, padx=10)
        
        # Add Select and Delete buttons below the table
        action_frame = tk.Frame(left_frame, bg="white")
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.inventory_select_btn = tk.Button(action_frame, text="Select", font=("Arial", 11),
                                             bg="#3b82f6", fg="white", width=12, cursor="hand2",
                                             command=self.toggle_inventory_selection)
        self.inventory_select_btn.pack(side=tk.LEFT, padx=5)
        
        self.inventory_delete_btn = tk.Button(action_frame, text="Delete", font=("Arial", 11),
                                             bg="#ef4444", fg="white", width=12, cursor="hand2",
                                             command=self.delete_selected_inventory, state=tk.DISABLED)
        self.inventory_delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.create_inventory_table(left_frame)
        
        right_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        tk.Label(right_frame, text="Add Details", font=("Arial", 16, "bold"),
                bg="white").pack(anchor=tk.W, padx=20, pady=20)
        
        self.create_add_form(right_frame)
    
    def toggle_inventory_selection(self):
        """Toggle between selection mode and normal mode"""
        if not self.inventory_selection_mode:
            # Enable selection mode
            self.inventory_selection_mode = True
            self.inventory_select_btn.config(text="Cancel", bg="#6b7280")
            self.inventory_delete_btn.config(state=tk.NORMAL)
            
            # Add checkboxes to the tree
            for item in self.inventory_tree.get_children():
                self.inventory_tree.item(item, tags=('unchecked',))
            
            self.inventory_tree.tag_configure('unchecked', foreground='black')
            self.inventory_tree.tag_configure('checked', foreground='blue', font=('Arial', 10, 'bold'))
            
            # Bind click event for selection
            self.inventory_tree.bind('<Button-1>', self.on_inventory_checkbox_click)
        else:
            # Disable selection mode
            self.inventory_selection_mode = False
            self.inventory_select_btn.config(text="Select", bg="#3b82f6")
            self.inventory_delete_btn.config(state=tk.DISABLED)
            
            # Remove all tags
            for item in self.inventory_tree.get_children():
                self.inventory_tree.item(item, tags=())
            
            self.inventory_checkboxes.clear()
            
            # Unbind click event
            self.inventory_tree.unbind('<Button-1>')
            self.inventory_tree.bind("<ButtonRelease-1>", self.on_product_click)
    
    def on_inventory_checkbox_click(self, event):
        """Handle checkbox click in inventory table"""
        if not self.inventory_selection_mode:
            return
        
        region = self.inventory_tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.inventory_tree.identify_row(event.y)
            if item:
                # Toggle selection
                if item in self.inventory_checkboxes:
                    del self.inventory_checkboxes[item]
                    self.inventory_tree.item(item, tags=('unchecked',))
                else:
                    self.inventory_checkboxes[item] = True
                    self.inventory_tree.item(item, tags=('checked',))
    
    def delete_selected_inventory(self):
        """Delete selected inventory items"""
        if not self.inventory_checkboxes:
            messagebox.showwarning("Warning", "No items selected")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {len(self.inventory_checkboxes)} selected item(s)?")
        if not confirm:
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            deleted_count = 0
            
            for item_id in self.inventory_checkboxes.keys():
                values = self.inventory_tree.item(item_id)['values']
                product_id = values[0]
                
                cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
                deleted_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            
            messagebox.showinfo("Success", f"{deleted_count} item(s) deleted successfully!")
            
            # Refresh the inventory table
            self.inventory_checkboxes.clear()
            self.toggle_inventory_selection()  # Exit selection mode
            self.load_inventory_data()
            
            # Refresh dashboard data
            self.data = self.fetch_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete items: {str(e)}")
            if conn:
                conn.close()
    
    def create_inventory_table(self, parent):
        table_frame = tk.Frame(parent, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        y_scroll = tk.Scrollbar(table_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("Product_id", "Product_name", "Category", "Quantity", "Price", "Supplier", "Created_at")
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                           yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=120)
        
        y_scroll.config(command=self.inventory_tree.yview)
        x_scroll.config(command=self.inventory_tree.xview)
        
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_inventory_data()
        
        self.inventory_tree.bind("<ButtonRelease-1>", self.on_product_click)
    
    def load_inventory_data(self):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT product_id, product_name, category, quantity, price, supplier, created_at
                    FROM products ORDER BY created_at DESC
                """)
                rows = cur.fetchall()
                
                for row in rows:
                    self.inventory_tree.insert("", tk.END, values=row)
                
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
                conn.close()
    
    def create_add_form(self, parent):
        form_frame = tk.Frame(parent, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        fields = [
            ("Product_ID", "product_id"),
            ("Product_Name", "product_name"),
            ("Category", "category"),
            ("Quantity", "quantity"),
            ("Price", "price"),
            ("Supplier", "supplier"),
            ("Created_at", "created_at")
        ]
        
        self.form_entries = {}
        
        for label, key in fields:
            tk.Label(form_frame, text=label, font=("Arial", 11),
                    bg="white", fg="#333").pack(anchor=tk.W, pady=(10, 2))
            
            if key == "category":
                category_container = tk.Frame(form_frame, bg="white")
                category_container.pack(fill=tk.X, pady=(0, 10))
                
                entry = tk.Entry(category_container, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1)
                entry.pack(fill=tk.X)
                self.form_entries[key] = entry
                
                self.category_listbox = tk.Listbox(category_container, height=3, font=("Arial", 10))
                self.category_listbox.pack(fill=tk.X)
                self.category_listbox.pack_forget()
                
                entry.bind("<KeyRelease>", self.on_category_change)
                self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)
            else:
                entry = tk.Entry(form_frame, font=("Arial", 12), bg="white",
                               relief=tk.SOLID, bd=1)
                entry.pack(fill=tk.X, pady=(0, 10))
                self.form_entries[key] = entry
                
                if key == "product_id":
                    entry.bind("<KeyRelease>", self.on_product_id_change)
        
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Clear", font=("Arial", 12),
                 bg="white", fg="#333", width=12, cursor="hand2",
                 relief=tk.SOLID, bd=1, command=self.clear_form).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Add", font=("Arial", 12),
                 bg="#4b9783", fg="white", width=12, cursor="hand2",
                 bd=0, command=self.add_product).pack(side=tk.LEFT, padx=10)
    
    def on_category_change(self, event):
        typed = self.form_entries['category'].get().lower()
        
        if not typed:
            self.category_listbox.pack_forget()
            return
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL")
                categories = [row[0] for row in cur.fetchall()]
                cur.close()
                conn.close()
                
                matching = [cat for cat in categories if typed in cat.lower()]
                
                if matching:
                    self.category_listbox.delete(0, tk.END)
                    for cat in matching[:5]:
                        self.category_listbox.insert(tk.END, cat)
                    self.category_listbox.pack(fill=tk.X)
                else:
                    self.category_listbox.pack_forget()
            except:
                conn.close()
    
    def on_category_select(self, event):
        selection = self.category_listbox.curselection()
        if selection:
            category = self.category_listbox.get(selection[0])
            self.form_entries['category'].delete(0, tk.END)
            self.form_entries['category'].insert(0, category)
            self.category_listbox.pack_forget()
    
    def on_product_id_change(self, event):
        product_id = self.form_entries['product_id'].get()
        if product_id:
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT product_name, category, quantity, price, supplier, created_at
                        FROM products WHERE product_id = %s
                    """, (product_id,))
                    result = cur.fetchone()
                    
                    if result:
                        # Product exists - fill all fields but keep them editable
                        self.form_entries['product_name'].delete(0, tk.END)
                        self.form_entries['product_name'].insert(0, result[0])
                        self.form_entries['product_name'].config(state='normal')  # Keep editable
                        
                        self.form_entries['category'].delete(0, tk.END)
                        self.form_entries['category'].insert(0, result[1])
                        self.form_entries['category'].config(state='normal')  # Keep editable
                        
                        self.form_entries['quantity'].delete(0, tk.END)
                        self.form_entries['quantity'].insert(0, result[2])
                        self.form_entries['quantity'].config(state='normal')
                        
                        self.form_entries['price'].delete(0, tk.END)
                        self.form_entries['price'].insert(0, result[3])
                        self.form_entries['price'].config(state='normal')  # Keep editable
                        
                        self.form_entries['supplier'].delete(0, tk.END)
                        self.form_entries['supplier'].insert(0, result[4])
                        self.form_entries['supplier'].config(state='normal')  # Keep editable
                        
                        self.form_entries['created_at'].delete(0, tk.END)
                        self.form_entries['created_at'].insert(0, result[5])
                        self.form_entries['created_at'].config(state='normal')  # Keep editable
                        
                        # Show info that product exists
                        self.form_entries['product_id'].config(bg="#fff3cd")  # Light yellow background
                    else:
                        # New product - enable all fields
                        self.form_entries['product_id'].config(bg="white")
                        for key in ['product_name', 'category', 'price', 'supplier', 'created_at']:
                            self.form_entries[key].config(state='normal')
                    
                    cur.close()
                    conn.close()
                except Exception as e:
                    if conn:
                        conn.close()
    
    def on_product_click(self, event):
        selection = self.inventory_tree.selection()
        if selection:
            item = self.inventory_tree.item(selection[0])
            values = item['values']
            
            self.clear_form()
            
            keys = ['product_id', 'product_name', 'category', 'quantity', 'price', 'supplier', 'created_at']
            for i, key in enumerate(keys):
                self.form_entries[key].insert(0, str(values[i]))
    
    def clear_form(self):
        for entry in self.form_entries.values():
            entry.config(state='normal')
            entry.delete(0, tk.END)
    
    def add_product(self):
        product_id = self.form_entries['product_id'].get().strip()
        product_name = self.form_entries['product_name'].get().strip()
        category = self.form_entries['category'].get().strip()
        quantity = self.form_entries['quantity'].get().strip()
        price = self.form_entries['price'].get().strip()
        supplier = self.form_entries['supplier'].get().strip()
        created_at = self.form_entries['created_at'].get().strip()  # ADD THIS
        
        if not product_id or not product_name or not quantity:
            messagebox.showerror("Error", "Product ID, Name and Quantity are required")
            return
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                messagebox.showerror("Error", "Quantity must be non-negative")
                return
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return
        
        try:
            price = float(price) if price else 0
            if price < 0:
                messagebox.showerror("Error", "Price must be non-negative")
                return
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            
            # Handle created_at date - use custom date or default to now
            if created_at and created_at != "YYYY-MM-DD (optional)":
                try:
                    from datetime import datetime
                    if len(created_at) == 10:
                        datetime.strptime(created_at, '%Y-%m-%d')
                        created_at_value = created_at + ' 00:00:00'
                    else:
                        datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        created_at_value = created_at
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format!\nUse: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS\nExample: 2025-10-21 or 2025-10-21 14:30:00")
                    cur.close()
                    conn.close()
                    return
            else:
                created_at_value = None  # Use database default
            
            # Check if product exists
            cur.execute("SELECT product_id, quantity FROM products WHERE product_id = %s", (product_id,))
            existing_product = cur.fetchone()
            
            if existing_product:
                # Product exists - ask user if they want to update or add quantity
                response = messagebox.askyesnocancel(
                    "Product Exists", 
                    f"Product '{product_id}' already exists.\n\n"
                    f"Click 'Yes' to UPDATE all product details\n"
                    f"Click 'No' to ADD quantity to existing stock\n"
                    f"Click 'Cancel' to abort"
                )
                
                if response is None:  # Cancel
                    cur.close()
                    conn.close()
                    return
                elif response:  # Yes - Update all details
                    if created_at_value:
                        cur.execute("""
                            UPDATE products 
                            SET product_name = %s, 
                                category = %s, 
                                quantity = %s, 
                                price = %s, 
                                supplier = %s,
                                created_at = %s
                            WHERE product_id = %s
                        """, (product_name, category, quantity, price, supplier, created_at_value, product_id))
                    else:
                        cur.execute("""
                            UPDATE products 
                            SET product_name = %s, 
                                category = %s, 
                                quantity = %s, 
                                price = %s, 
                                supplier = %s,
                                created_at = CURRENT_TIMESTAMP
                            WHERE product_id = %s
                        """, (product_name, category, quantity, price, supplier, product_id))
                    messagebox.showinfo("Success", f"Product '{product_id}' updated successfully!\nAll details have been modified.")
                else:  # No - Add to quantity
                    old_quantity = existing_product[1]
                    new_quantity = old_quantity + quantity
                    cur.execute("""
                        UPDATE products 
                        SET quantity = %s
                        WHERE product_id = %s
                    """, (new_quantity, product_id))
                    messagebox.showinfo("Success", f"Product quantity updated!\n{old_quantity} → {new_quantity} (+{quantity})")
            else:
                # New product - Insert
                if created_at_value:
                    cur.execute("""
                        INSERT INTO products (product_id, product_name, category, quantity, price, supplier, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (product_id, product_name, category, quantity, price, supplier, created_at_value))
                else:
                    cur.execute("""
                        INSERT INTO products (product_id, product_name, category, quantity, price, supplier)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (product_id, product_name, category, quantity, price, supplier))
                messagebox.showinfo("Success", f"Product '{product_id}' added successfully!")
            
            conn.commit()
            cur.close()
            conn.close()
            
            # Clear form and reload data
            self.clear_form()
            self.load_inventory_data()
            
            # Refresh dashboard
            self.data = self.fetch_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add/update product: {str(e)}")
            if conn:
                conn.rollback()
                conn.close()
    
    def get_status_color(self, value, threshold_good, threshold_bad, reverse=False):
        if reverse:
            return "#4ade80" if value < threshold_good else "#ef4444"
        else:
            return "#4ade80" if value >= threshold_good else "#ef4444" if value < threshold_bad else "#fbbf24"
    
    def show_notifications(self):
        popup = tk.Toplevel(self.root)
        popup.title("Notifications")
        popup.geometry("450x500")
        popup.configure(bg="white")
        
        tk.Label(popup, text="Notifications", font=("Arial", 14, "bold"),
                bg="white").pack(pady=10)
        
        if not self.notifications:
            tk.Label(popup, text="✅ No notifications\nEverything looks good!",
                    font=("Arial", 12), bg="white", fg="#4ade80").pack(pady=50)
        else:
            # Create canvas with scrollbar
            canvas = tk.Canvas(popup, bg="white")
            scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="white")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=420)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Add notifications to scrollable frame
            for notif in self.notifications:
                notif_frame = tk.Frame(scrollable_frame, bg="#fef3c7", relief=tk.RAISED, bd=1)
                notif_frame.pack(fill=tk.X, pady=5, padx=10)
                
                tk.Label(notif_frame, text=notif, font=("Arial", 10),
                        bg="#fef3c7", fg="#92400e", wraplength=380,
                        justify=tk.LEFT).pack(padx=10, pady=10, anchor=tk.W)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 20))
            
            # Enable mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Unbind when window closes
            def on_closing():
                canvas.unbind_all("<MouseWheel>")
                popup.destroy()
            
            popup.protocol("WM_DELETE_WINDOW", on_closing)

    def show_settings(self):
        popup = tk.Toplevel(self.root)
        popup.title("Settings")
        popup.geometry("350x700")  # Increased height
        popup.configure(bg="white")
        
        tk.Label(popup, text="Settings", font=("Arial", 14, "bold"),
                bg="white").pack(pady=20)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(popup, bg="white")
        scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=320)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame inside scrollable frame
        btn_frame = tk.Frame(scrollable_frame, bg="white")
        btn_frame.pack(expand=True, pady=20)
        
        if self.role == "Admin":
            add_employee_btn = tk.Button(btn_frame, text="➕ Add Employee", font=("Arial", 12),
                                        bg="#4b9783", fg="white", width=18, cursor="hand2",
                                        command=self.add_employee)
            add_employee_btn.pack(pady=10)
            
            view_employee_btn = tk.Button(btn_frame, text="👥 View Employees", font=("Arial", 12),
                                         bg="#4b9783", fg="white", width=18, cursor="hand2",
                                         command=self.view_employees)
            view_employee_btn.pack(pady=10)
            
            view_issues_btn = tk.Button(btn_frame, text="📧 View Contact Issues", font=("Arial", 12),
                                       bg="#4b9783", fg="white", width=18, cursor="hand2",
                                       command=self.view_contact_issues)
            view_issues_btn.pack(pady=10)
            
            # ADD DOWNLOAD BUTTON
            download_btn = tk.Button(btn_frame, text="📥 Download Data", font=("Arial", 12),
                                    bg="#3b82f6", fg="white", width=18, cursor="hand2",
                                    command=self.download_all_data)
            download_btn.pack(pady=10)
        
        settings_btn = tk.Button(btn_frame, text="⚙️ Settings", font=("Arial", 12),
                                bg="#3b82f6", fg="white", width=18, cursor="hand2",
                                command=self.open_user_settings)
        settings_btn.pack(pady=10)
        
        logout_btn = tk.Button(btn_frame, text="🚪 Logout", font=("Arial", 12),
                              bg="#ef4444", fg="white", width=18, cursor="hand2",
                              command=self.logout)
        logout_btn.pack(pady=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 15))
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind when window closes
        def on_closing():
            canvas.unbind_all("<MouseWheel>")
            popup.destroy()
        
        popup.protocol("WM_DELETE_WINDOW", on_closing)

    def download_all_data(self):
        """Export all database tables to Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            import os
        except ImportError:
            messagebox.showerror("Error", "Required libraries not found!\n\nPlease install:\npip install pandas openpyxl")
            return
        
        # Ask user where to save
        from tkinter import filedialog
        
        # Default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"Inventory_Data_{timestamp}.xlsx"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Save Database Export"
        )
        
        if not filepath:
            return  # User cancelled
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Export Products table
                try:
                    products_df = pd.read_sql_query("SELECT * FROM products ORDER BY product_id", conn)
                    if not products_df.empty:
                        products_df.to_excel(writer, sheet_name='Products', index=False)
                except Exception as e:
                    print(f"Products export error: {e}")
                    products_df = pd.DataFrame()
                
                # Export Sales table with user names
                try:
                    sales_df = pd.read_sql_query("""
                        SELECT s.*, u.user_name 
                        FROM sales s 
                        LEFT JOIN users u ON s.user_id = u.user_id 
                        ORDER BY s.sales_date DESC
                    """, conn)
                    if not sales_df.empty:
                        sales_df.to_excel(writer, sheet_name='Sales', index=False)
                except Exception as e:
                    print(f"Sales export error: {e}")
                    sales_df = pd.DataFrame()
                
                # Export Purchases table
                try:
                    purchases_df = pd.read_sql_query("SELECT * FROM purchases ORDER BY purchase_date DESC", conn)
                    if not purchases_df.empty:
                        purchases_df.to_excel(writer, sheet_name='Purchases', index=False)
                except Exception as e:
                    print(f"Purchases export error: {e}")
                    purchases_df = pd.DataFrame()
                
                # Export Employees table (exclude password for security)
                try:
                    employees_df = pd.read_sql_query("SELECT * FROM employees ORDER BY employee_id", conn)
                    if not employees_df.empty:
                        # Remove password column if it exists
                        if 'password' in employees_df.columns:
                            employees_df = employees_df.drop(columns=['password'])
                        employees_df.to_excel(writer, sheet_name='Employees', index=False)
                except Exception as e:
                    print(f"Employees export error: {e}")
                    employees_df = pd.DataFrame()
                
                # Export Users table
                try:
                    users_df = pd.read_sql_query("SELECT * FROM users ORDER BY user_id", conn)
                    if not users_df.empty:
                        users_df.to_excel(writer, sheet_name='Users', index=False)
                except Exception as e:
                    print(f"Users export error: {e}")
                    users_df = pd.DataFrame()
                
                # Export Contact Issues (if admin)
                if self.role == "Admin":
                    try:
                        issues_df = pd.read_sql_query("SELECT * FROM contact_issues ORDER BY created_at DESC", conn)
                        if not issues_df.empty:
                            issues_df.to_excel(writer, sheet_name='Contact_Issues', index=False)
                    except Exception as e:
                        print(f"Contact issues export error: {e}")
                        issues_df = pd.DataFrame()
                
                # Export Admin Notifications (if admin)
                if self.role == "Admin":
                    try:
                        notif_df = pd.read_sql_query("SELECT * FROM admin_notifications ORDER BY created_at DESC", conn)
                        if not notif_df.empty:
                            # Remove sensitive password info if present
                            if 'new_password' in notif_df.columns:
                                notif_df = notif_df.drop(columns=['new_password'])
                            notif_df.to_excel(writer, sheet_name='Notifications', index=False)
                    except Exception as e:
                        print(f"Notifications export error: {e}")
                
                # Create Summary sheet with statistics
                summary_data = {
                    'Metric': [
                        'Total Products',
                        'Total Quantity in Stock',
                        'Total Sales Records',
                        'Total Revenue',
                        'Total Purchase Records',
                        'Total Purchase Cost',
                        'Total Employees',
                        'Total Customers',
                        'Export Date',
                        'Exported By'
                    ],
                    'Value': [
                        len(products_df) if not products_df.empty else 0,
                        int(products_df['quantity'].sum()) if not products_df.empty and 'quantity' in products_df.columns else 0,
                        len(sales_df) if not sales_df.empty else 0,
                        f"${float(sales_df['total_amount'].sum()):.2f}" if not sales_df.empty and 'total_amount' in sales_df.columns else "$0.00",
                        len(purchases_df) if not purchases_df.empty else 0,
                        f"${float(purchases_df['total_cost'].sum()):.2f}" if not purchases_df.empty and 'total_cost' in purchases_df.columns else "$0.00",
                        len(employees_df) if not employees_df.empty else 0,
                        len(users_df) if not users_df.empty else 0,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        self.username
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            conn.close()
            
            # Success message with option to open file
            response = messagebox.askyesno(
                "Success", 
                f"Data exported successfully!\n\nFile saved to:\n{filepath}\n\nDo you want to open the file?"
            )
            
            if response:
                try:
                    os.startfile(filepath)  # Windows
                except AttributeError:
                    try:
                        os.system(f'open "{filepath}"')  # macOS
                    except:
                        os.system(f'xdg-open "{filepath}"')  # Linux
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")
            if conn:
                conn.close()
    
    def add_employee(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Employee")
        popup.geometry("400x400")
        popup.configure(bg="white")
        
        tk.Label(popup, text="Add New Employee", font=("Arial", 14, "bold"),
                bg="white").pack(pady=20)
        
        form_frame = tk.Frame(popup, bg="white")
        form_frame.pack(padx=30, pady=10)
        
        tk.Label(form_frame, text="Employee ID:", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        emp_id_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        emp_id_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Employee Name:", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        emp_name_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        emp_name_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Email (Optional):", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        emp_email_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        emp_email_entry.pack(pady=5)
        
        def submit_employee():
            emp_id = emp_id_entry.get().strip()
            emp_name = emp_name_entry.get().strip()
            emp_email = emp_email_entry.get().strip()
            
            if not emp_id:
                messagebox.showerror("Error", "Employee ID is required")
                return
            
            # Convert empty email to None for database
            if not emp_email:
                emp_email = None
            
            password = f"{emp_id}@123"
            
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    
                    # Create table if not exists with proper email constraint
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS employees (
                            employee_id VARCHAR(50) PRIMARY KEY,
                            employee_name VARCHAR(100),
                            email VARCHAR(100) UNIQUE,
                            password VARCHAR(100) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Check if employee ID already exists
                    cur.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (emp_id,))
                    if cur.fetchone():
                        messagebox.showerror("Error", "Employee ID already exists")
                        cur.close()
                        conn.close()
                        return
                    
                    # Check if email already exists (only if email is provided)
                    if emp_email:
                        cur.execute("SELECT employee_id FROM employees WHERE email = %s", (emp_email,))
                        if cur.fetchone():
                            messagebox.showerror("Error", "Email already exists. Please use a different email.")
                            cur.close()
                            conn.close()
                            return
                    
                    # Insert new employee
                    cur.execute("""
                        INSERT INTO employees (employee_id, employee_name, email, password)
                        VALUES (%s, %s, %s, %s)
                    """, (emp_id, emp_name, emp_email, password))
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    messagebox.showinfo("Success", f"Employee added!\nUsername: {emp_id}\nPassword: {password}")
                    popup.destroy()
                    
                except psycopg2.IntegrityError as e:
                    if 'employee_email_key' in str(e) or 'email' in str(e).lower():
                        messagebox.showerror("Error", "Email already exists. Please use a different email.")
                    elif 'employee_pkey' in str(e) or 'employee_id' in str(e).lower():
                        messagebox.showerror("Error", "Employee ID already exists.")
                    else:
                        messagebox.showerror("Error", f"Failed to add employee: {str(e)}")
                    if conn:
                        conn.rollback()
                        conn.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add employee: {str(e)}")
                    if conn:
                        conn.rollback()
                        conn.close()
        
        tk.Button(form_frame, text="Add Employee", font=("Arial", 12),
                 bg="#4b9783", fg="white", width=15, cursor="hand2",
                 command=submit_employee).pack(pady=20)
    
    def view_employees(self):
        popup = tk.Toplevel(self.root)
        popup.title("View Employees")
        popup.geometry("800x600")
        popup.configure(bg="white")
        
        tk.Label(popup, text="Employee List", font=("Arial", 14, "bold"),
                bg="white").pack(pady=20)
        
        # Add Select and Delete buttons for employees
        action_frame = tk.Frame(popup, bg="white")
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.employee_select_btn = tk.Button(action_frame, text="Select", font=("Arial", 11),
                                            bg="#3b82f6", fg="white", width=12, cursor="hand2",
                                            command=self.toggle_employee_selection)
        self.employee_select_btn.pack(side=tk.LEFT, padx=5)
        
        self.employee_delete_btn = tk.Button(action_frame, text="Delete", font=("Arial", 11),
                                            bg="#ef4444", fg="white", width=12, cursor="hand2",
                                            command=self.delete_selected_employees, state=tk.DISABLED)
        self.employee_delete_btn.pack(side=tk.LEFT, padx=5)
        
        table_frame = tk.Frame(popup, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        y_scroll = tk.Scrollbar(table_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("Employee ID", "Name", "Email")
        self.employee_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=250)
        
        y_scroll.config(command=self.employee_tree.yview)
        x_scroll.config(command=self.employee_tree.xview)
        
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_employee_data()
        
        tk.Button(popup, text="Close", font=("Arial", 12),
                 bg="#6b7280", fg="white", width=15, cursor="hand2",
                 command=popup.destroy).pack(pady=20)
    
    def load_employee_data(self):
        """Load employee data into the treeview"""
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT employee_id, employee_name, COALESCE(email, 'N/A')
                    FROM employees ORDER BY employee_id
                """)
                rows = cur.fetchall()
                
                for row in rows:
                    self.employee_tree.insert("", tk.END, values=row)
                
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load employees: {str(e)}")
                if conn:
                    conn.close()
    
    def toggle_employee_selection(self):
        """Toggle between selection mode and normal mode for employees"""
        if not self.employee_selection_mode:
            # Enable selection mode
            self.employee_selection_mode = True
            self.employee_select_btn.config(text="Cancel", bg="#6b7280")
            self.employee_delete_btn.config(state=tk.NORMAL)
            
            # Add checkboxes to the tree
            for item in self.employee_tree.get_children():
                self.employee_tree.item(item, tags=('unchecked',))
            
            self.employee_tree.tag_configure('unchecked', foreground='black')
            self.employee_tree.tag_configure('checked', foreground='blue', font=('Arial', 10, 'bold'))
            
            # Bind click event for selection
            self.employee_tree.bind('<Button-1>', self.on_employee_checkbox_click)
        else:
            # Disable selection mode
            self.employee_selection_mode = False
            self.employee_select_btn.config(text="Select", bg="#3b82f6")
            self.employee_delete_btn.config(state=tk.DISABLED)
            
            # Remove all tags
            for item in self.employee_tree.get_children():
                self.employee_tree.item(item, tags=())
            
            self.employee_checkboxes.clear()
            
            # Unbind click event
            self.employee_tree.unbind('<Button-1>')
    
    def on_employee_checkbox_click(self, event):
        """Handle checkbox click in employee table"""
        if not self.employee_selection_mode:
            return
        
        region = self.employee_tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.employee_tree.identify_row(event.y)
            if item:
                # Toggle selection
                if item in self.employee_checkboxes:
                    del self.employee_checkboxes[item]
                    self.employee_tree.item(item, tags=('unchecked',))
                else:
                    self.employee_checkboxes[item] = True
                    self.employee_tree.item(item, tags=('checked',))
    
    def delete_selected_employees(self):
        """Delete selected employees"""
        if not self.employee_checkboxes:
            messagebox.showwarning("Warning", "No employees selected")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {len(self.employee_checkboxes)} selected employee(s)?")
        if not confirm:
            return
        
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cur = conn.cursor()
            deleted_count = 0
            
            for item_id in self.employee_checkboxes.keys():
                values = self.employee_tree.item(item_id)['values']
                employee_id = values[0]
                
                cur.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
                deleted_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            
            messagebox.showinfo("Success", f"{deleted_count} employee(s) deleted successfully!")
            
            # Refresh the employee table
            self.employee_checkboxes.clear()
            self.toggle_employee_selection()  # Exit selection mode
            self.load_employee_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete employees: {str(e)}")
            if conn:
                conn.close()
    
    def view_contact_issues(self):
        """View all contact issues submitted by users"""
        popup = tk.Toplevel(self.root)
        popup.title("Contact Issues")
        popup.geometry("900x600")
        popup.configure(bg="white")
        
        tk.Label(popup, text="Contact Issues", font=("Arial", 14, "bold"),
                bg="white").pack(pady=20)
        
        # Action buttons
        action_frame = tk.Frame(popup, bg="white")
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def refresh_issues():
            load_issues()
        
        def mark_resolved():
            selection = issues_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an issue")
                return
            
            issue_id = issues_tree.item(selection[0])['values'][0]
            
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE contact_issues 
                        SET status = 'Resolved', read = true 
                        WHERE id = %s
                    """, (issue_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    messagebox.showinfo("Success", "Issue marked as resolved")
                    refresh_issues()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update: {str(e)}")
                    if conn:
                        conn.close()
        
        tk.Button(action_frame, text="🔄 Refresh", font=("Arial", 11),
                 bg="#3b82f6", fg="white", width=12, cursor="hand2",
                 command=refresh_issues).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="✓ Mark Resolved", font=("Arial", 11),
                 bg="#4ade80", fg="white", width=12, cursor="hand2",
                 command=mark_resolved).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_frame = tk.Frame(popup, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        y_scroll = tk.Scrollbar(table_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("ID", "Email", "Issue", "Submitted By", "Status", "Date")
        issues_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                   yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        issues_tree.heading("ID", text="ID")
        issues_tree.heading("Email", text="Email")
        issues_tree.heading("Issue", text="Issue")
        issues_tree.heading("Submitted By", text="Submitted By")
        issues_tree.heading("Status", text="Status")
        issues_tree.heading("Date", text="Date")
        
        issues_tree.column("ID", width=50)
        issues_tree.column("Email", width=150)
        issues_tree.column("Issue", width=300)
        issues_tree.column("Submitted By", width=100)
        issues_tree.column("Status", width=80)
        issues_tree.column("Date", width=150)
        
        y_scroll.config(command=issues_tree.yview)
        x_scroll.config(command=issues_tree.xview)
        
        issues_tree.pack(fill=tk.BOTH, expand=True)
        
        def load_issues():
            for item in issues_tree.get_children():
                issues_tree.delete(item)
            
            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT id, email, issue, submitted_by, status, created_at
                        FROM contact_issues 
                        ORDER BY created_at DESC
                    """)
                    rows = cur.fetchall()
                    
                    for row in rows:
                        issue_preview = row[2][:80] + "..." if len(row[2]) > 80 else row[2]
                        display_row = (row[0], row[1], issue_preview, row[3], row[4], row[5])
                        issues_tree.insert("", tk.END, values=display_row)
                    
                    cur.close()
                    conn.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load issues: {str(e)}")
                    if conn:
                        conn.close()
        
        load_issues()
        
        tk.Button(popup, text="Close", font=("Arial", 12),
                 bg="#6b7280", fg="white", width=15, cursor="hand2",
                 command=popup.destroy).pack(pady=20)

    def open_user_settings(self):
        popup = tk.Toplevel(self.root)
        popup.title("User Settings")
        popup.geometry("400x450")
        popup.configure(bg="white")
        
        tk.Label(popup, text="User Settings", font=("Arial", 14, "bold"),
                bg="white").pack(pady=20)
        
        form_frame = tk.Frame(popup, bg="white")
        form_frame.pack(padx=30, pady=10)
        
        tk.Label(form_frame, text="Name:", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        name_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        name_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Email:", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        email_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        email_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Current Password:", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        current_pass = tk.Entry(form_frame, font=("Arial", 12), width=30, show="*")
        current_pass.pack(pady=5)
        
        tk.Label(form_frame, text="New Password:", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        new_pass = tk.Entry(form_frame, font=("Arial", 12), width=30, show="*")
        new_pass.pack(pady=5)
        
        tk.Label(form_frame, text="Confirm Password:", font=("Arial", 11), bg="white").pack(anchor=tk.W, pady=5)
        confirm_pass = tk.Entry(form_frame, font=("Arial", 12), width=30, show="*")
        confirm_pass.pack(pady=5)
        
        def save_settings():
            messagebox.showinfo("Success", "Settings updated successfully!")
            popup.destroy()
        
        tk.Button(form_frame, text="Save Changes", font=("Arial", 12),
                 bg="#4b9783", fg="white", width=15, cursor="hand2",
                 command=save_settings).pack(pady=20)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.configure(bg="#4b9783")
            LoginPage(self.root, self.on_login_success_callback)
    
    def on_login_success_callback(self, role, username):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg="#f5f5f5")
        InventoryDashboard(self.root, role, username)

def main():
    root = tk.Tk()
    root.title("Inventory Management System")
    root.geometry("1366x768")
    root.configure(bg="#4b9783")
    
    def on_login(role, username):
        for widget in root.winfo_children():
            widget.destroy()
        root.configure(bg="#f5f5f5")
        InventoryDashboard(root, role, username)
    
    LoginPage(root, on_login)
    root.mainloop()

if __name__ == "__main__":
    main()







