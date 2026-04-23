# Smart Retail Inventory & VMI Manager 🛠️

**A Streamlit and Pandas application built to automate hardware store inventory ordering, manage vendor budgets, and clean messy Point-of-Sale data.**

## 📌 The Business Problem
Managing weekly inventory orders for a retail hardware store is traditionally a highly manual, error-prone process. The existing workflow required exporting messy, unstructured CSV reports from a legacy POS system (RockSolid), manually comparing 60-day and 30-day seasonal sales velocities against current Quantity on Hand (QOH), and manually isolating specific Vendor-Managed Inventory (VMI) items, all while trying to stay under a strict weekly budget.

## 🚀 The Solution
I developed a local web application using Python and Streamlit that completely automates this workflow. The app ingests raw POS exports (from Rock Office Manager), forcefully cleans the data, runs predictive inventory algorithms, and outputs perfectly formatted bulk-upload CSVs for the primary distributor (Do It Best).

### Key Features:
* **Custom Data Cleaning Pipeline:** Built a Pandas cleaning function that automatically detects and realigns shifted CSV columns caused by missing vendor data in the legacy POS exports.
* **Regex Filtering:** Utilizes Regular Expressions to scrub page breaks, hidden strings, and invalid SKU formats out of the raw data.
* **Automated VMI Segregation:** Automatically detects and isolates "Hillman" vendor items, removing them from the primary order and calculating a separate monthly reserve budget for the sales rep.
* **Predictive Ordering Logic:** Calculates target stock levels by comparing recent 60-day sales velocity against historical 30-day seasonal velocity. 
* **Dynamic Budget Enforcement:** Ranks all needed items by a priority score (Expected Velocity / Unit Cost) and cuts off the generated order the exact moment the user-defined budget is hit.

## 💻 Technical Stack
* **Language:** Python
* **Libraries:** Pandas (Data manipulation), NumPy (Mathematical comparisons), Streamlit (Frontend UI/UX), Datetime
* **Concepts:** Data Cleaning, Regex, Boolean Indexing, Budget Optimization, VMI (Vendor-Managed Inventory)

## 📸 Application Preview
*(Insert a screenshot of your Streamlit app running here)*

## 📈 Business Impact
* **Time Saved:** Reduced a multi-hour Monday morning ordering process into a 3-minute drag-and-drop workflow.
* **Financial Control:** Ensured the store strictly adheres to its dynamic weekly spending limits without understocking high-priority items.
* **Data Integrity:** Eliminated catalog upload errors by ensuring only valid, 6-digit SKUs make it to the final Do It Best order.
