# 🧾 Inventory Management System (Python + Tkinter + PostgreSQL)

This is a **desktop Inventory Management System** built with **Python Tkinter** and a **PostgreSQL database**, designed to let **Admins** and **Employees** manage products, sales, purchases, users, and issues through a clean sidebar-based interface with real-time analytics and charts.


## 🚀 Features

### 🔐 Role-based Login
- Admin and Employee roles with different access rights.
- “Remember Me” and “Forgot Password” functionality.
- Admin recovery wizard and Employee password reset notification system.

### 📦 Inventory Management
- Add, update, and delete products with live stock synchronization.
- KPI cards that change colors dynamically based on stock levels.
- Export complete database (Products, Sales, Purchases, Users, Employees) to Excel.

### 💰 Sales & Purchases
- Smart validation of stock and employee details.
- Auto-adjust stock quantities on every sale or purchase.
- Editable records with change tracking and safeguards.
- Year-wise *Expenses vs Revenue* analytics.

### 📊 Dashboard Analytics
- KPI cards: Total Products, Quantity Sold, Revenue, Purchases, Customers.
- Pie Chart: Available vs Sold Units.
- Bar Chart: Top 10 Products by Sales.
- Line Chart: Monthly Expenses vs Revenue for the current year.

### ⚙️ Maintenance & Notifications
- Tracks admin notifications and employee issues.
- Displays unread items with alert badges.
- Editable user settings and secure logout.


## 🧱 Built With

| Component | Technology |
|------------|-------------|
| **Frontend (UI)** | Python Tkinter |
| **Backend (Logic)** | Python |
| **Database** | PostgreSQL |
| **Data Connector** | psycopg2 |
| **Analytics & Charts** | Matplotlib |
| **Data Handling / Export** | Pandas |
| **UI Design Style** | Minimal Sidebar Dashboard (Custom Tkinter Frames) |


## 📂 Database Tables
- **products** – product_id, product_name, category, price, quantity  
- **sales** – sales_id, product_id, employee_id, quantity_sold, total_amount, sales_date, user_id  
- **purchases** – purchase_id, product_id, quantity_purchased, total_cost, purchase_date, supplier  
- **users** – user_id, user_name, email  
- **employees** – employee_id, name, email, password, role  
- **admin_notifications**, **contact_issues**


## 🖼️ UI Overview

### Login Screen
<img width="1919" height="1019" alt="Screenshot 2025-10-22 205933" src="https://github.com/user-attachments/assets/42dec52d-6ba1-45de-a210-ccfee738883a" />

### Dashboard
<img width="1919" height="1017" alt="Screenshot 2025-10-22 210000" src="https://github.com/user-attachments/assets/66e73449-5023-4f77-9a19-d6f4f07f3a98" />
<img width="1919" height="1019" alt="Screenshot 2025-10-22 210013" src="https://github.com/user-attachments/assets/a481a0f8-30c4-47c6-9897-a7cf6334e054" />

### Inventory Page
<img width="1919" height="1019" alt="Screenshot 2025-10-22 210026" src="https://github.com/user-attachments/assets/31671afb-54fa-4dcc-a2dc-75830f59fd54" />

### Sales Page
<img width="1919" height="1019" alt="Screenshot 2025-10-22 210039" src="https://github.com/user-attachments/assets/628b58c9-1e4f-458e-bc28-714c86d8f5c1" />

### Purchases Page
<img width="1919" height="1018" alt="Screenshot 2025-10-22 210050" src="https://github.com/user-attachments/assets/fb2b287e-44ef-4d7d-83de-88873b3ace1e" />

### Contact Page
<img width="1919" height="1017" alt="Screenshot 2025-10-22 210101" src="https://github.com/user-attachments/assets/4bc676bb-076c-4cc4-81a0-a2b705c62448" />


## 🎥 Presentation Video

- <a href="https://youtu.be/C4sS37TT3NA?si=qnMSLTuvKGW8IUdA">Watch the Presentation here</a>

The video walkthrough explains:
- App navigation (Login → Dashboard → Inventory → Sales → Purchase)
- How sales/purchases auto-update product stock
- Dashboard analytics (Top Products, Revenue vs Expenses)
- Smart search and notifications in action


## ⚙️ How to Run

1. **Clone this repository**
   ```bash
   git clone https://github.com/<your-username>/inventory-management-system-tkinter.git
   cd inventory-management-system-tkinter


## 🗣️ Let’s Talk

I’d love to connect and discuss tech, data, and product ideas!

** Shobith Ramesh**  
Navi Mumbai, India  

🔗 [LinkedIn](https://www.linkedin.com/in/shobithramesh)  
📫 shobithramesh96@gmail.com  
