Smart Retail Inventory & VMI Engine 🛠️
A production-ready Streamlit and Pandas web application built to automate hardware store inventory ordering, execute dynamic Min/Max replenishment logic, and enforce strict budget parameters using raw Point-of-Sale data.

📌 The Business Problem
Managing weekly inventory orders for a high-volume retail hardware store is traditionally a manual, error-prone process. The existing workflow required exporting messy, unstructured CSV reports from a legacy POS system (RockSolid) and manually comparing 60-day and 30-day seasonal sales velocities against current Quantity on Hand (QOH). This process lacked historical context, routinely risked ordering "dead" discontinued inventory, and made it nearly impossible to maximize weekly spending budgets efficiently while isolating specific Vendor-Managed Inventory (VMI).

🚀 The Solution
I developed a local web application using Python and Streamlit that operates as a central data pipeline for retail operations. The app ingests raw POS exports, dynamically cleans the data, runs predictive inventory algorithms to establish dynamic safety stock lines, and outputs perfectly formatted bulk-upload CSVs for the primary distributor (Do It Best).

Key Features:
Dynamic Min/Max Replenishment: Calculates a "Peak Velocity" by cross-referencing recent 60-day, seasonal 30-day, and full yearly sales. Automatically generates a Dynamic Reorder Point (MIN) and Order-Up-To Level (MAX) customized to every single SKU's unique sales speed.

Tiered Waterfall Budgeting: Utilizes a custom algorithmic priority score to fully fund fast-moving "A-Tier" items first. It then cascades remaining budget dollars to systematically fill out-of-stock "B-Tier" items based on their historical yearly sales volume, cleanly cutting off the moment the exact budget limit is reached.

Dead Inventory Purging: Explicitly penalizes and drops items with zero recent and zero historical sales, completely eliminating budget waste on invalid or discontinued SKUs.

Bulletproof Data Cleaning Pipeline: A custom Pandas cleaning function that automatically detects and realigns shifted CSV columns caused by missing vendor data in legacy POS exports, seamlessly handling both raw and manually cleaned files without crashing.

Automated VMI Segregation: Automatically detects and isolates "Hillman" vendor items, removing them from the primary order and calculating a separate monthly reserve budget for the sales rep.

Automated Local Context: Silently ingests static yearly sales data from the local directory, providing long-term historical context to the math engine without requiring the user to constantly re-upload massive yearly datasets.

💻 Technical Stack
Language: Python

Libraries: Pandas (Data manipulation & pure vectorization), NumPy (Complex algorithmic comparisons), Streamlit (Frontend UI/UX), Datetime, OS

Concepts: Dynamic Inventory Replenishment, Budget Optimization, Data Cleaning, Regex, Boolean Indexing, VMI (Vendor-Managed Inventory)

📸 Application Preview
(Insert a screenshot of your Streamlit app running here, ideally showing the budget dials and the final success message!)

📈 Business Impact
Time Saved: Reduced a multi-hour manual ordering process into a 60-second drag-and-drop workflow.

Financial Optimization: Replaced static ordering with a Waterfall Budget algorithm, ensuring the store strictly adheres to dynamic weekly spending limits while mathematically maximizing the utility of every dollar spent.

Data Integrity: Eliminated catalog upload errors by ensuring only valid, actively selling 6-digit SKUs make it to the final distributor order pipeline.
