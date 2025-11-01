import base64
import os
from io import BytesIO

import matplotlib.pyplot as plt
import polars as pl

from utils import get_project_root, ensure_directory_exists


def create_pie_chart(analysis_data: dict) -> str:
    labels = ["Balanced", "Overpaid", "Underpaid"]
    sizes = [
        analysis_data["balanced"]["count"],
        analysis_data["overpaid"]["count"],
        analysis_data["underpaid"]["count"],
    ]
    colors = ["#28a745", "#dc3545", "#ffc107"]  # Green, Red, Yellow

    plt.figure(figsize=(5, 3.5))
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    plt.title(
        "Claims Reconciliation Status Distribution", fontsize=12, fontweight="bold"
    )
    plt.axis("equal")

    # Convert to base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close()

    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{image_base64}"


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def generate_summary_section(analysis_data: dict, chart_image: str) -> str:
    return f"""
    <div class="summary-section">
        <h2>📊 Reconciliation Summary</h2>
        <div class="summary-content">
            <div class="summary-cards">
                <div class="summary-grid">
                    <div class="summary-card total">
                        <h3>Total Claims</h3>
                        <div class="number">{analysis_data['total_claims']:,}</div>
                    </div>
                    
                    <div class="summary-card balanced">
                        <h3>✅ Balanced Claims</h3>
                        <div class="number">{analysis_data['balanced']['count']:,}</div>
                        <div class="percentage">({analysis_data['balanced']['percentage']}%)</div>
                    </div>
                    
                    <div class="summary-card overpaid">
                        <h3>⬆️ Overpaid Claims</h3>
                        <div class="number">{analysis_data['overpaid']['count']:,}</div>
                        <div class="percentage">({analysis_data['overpaid']['percentage']}%)</div>
                        <div class="amount">{format_currency(analysis_data['overpaid']['amount'])}</div>
                    </div>
                    
                    <div class="summary-card underpaid">
                        <h3>⬇️ Underpaid Claims</h3>
                        <div class="number">{analysis_data['underpaid']['count']:,}</div>
                        <div class="percentage">({analysis_data['underpaid']['percentage']}%)</div>
                        <div class="amount">{format_currency(analysis_data['underpaid']['amount'])}</div>
                    </div>
                    
                    <div class="summary-card issues">
                        <h3>⚠️ Total Issues</h3>
                        <div class="number">{analysis_data['total_overpaid_and_underpaid_claims']['count']:,}</div>
                        <div class="percentage">({analysis_data['total_overpaid_and_underpaid_claims']['percentage']}%)</div>
                        <div class="amount">{format_currency(analysis_data['total_overpaid_and_underpaid_claims']['amount'])}</div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <img src="{chart_image}" alt="Claims Distribution Pie Chart">
            </div>
        </div>
    </div>
    """


def generate_table_data(reconciled_df: pl.DataFrame) -> str:
    rows = []
    for row in reconciled_df.iter_rows(named=True):
        status_class = row["reconciliation_status"].lower()
        rows.append(
            f"""
            <tr class="table-row {status_class}" data-status="{row['reconciliation_status']}">
                <td>{row['claim_id']}</td>
                <td>{row['patient_id']}</td>
                <td>{format_currency(row['charges_amount'])}</td>
                <td>{format_currency(row['benefit_amount'])}</td>
                <td>{format_currency(row['total_transaction_value'])}</td>
                <td><span class="status-badge {status_class}">{row['reconciliation_status']}</span></td>
            </tr>
        """
        )
    return "".join(rows)


def generate_html_report(
    reconciled_df: pl.DataFrame, analysis_data: dict, chart_image: str
) -> str:
    table_rows = generate_table_data(reconciled_df)
    summary_section = generate_summary_section(analysis_data, chart_image)

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Insurance Reconciliation Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 15px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .summary-card {{
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid;
        }}
        
        .summary-card.total {{ background: #e8f4fd; border-color: #007bff; }}
        .summary-card.balanced {{ background: #e8f5e8; border-color: #28a745; }}
        .summary-card.overpaid {{ background: #fdeaea; border-color: #dc3545; }}
        .summary-card.underpaid {{ background: #fff3cd; border-color: #ffc107; }}
        .summary-card.issues {{ background: #f8d7da; border-color: #dc3545; }}
        
        .summary-card h3 {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
        }}
        
        .summary-card .number {{
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }}
        
        .summary-card .percentage {{
            font-size: 0.9rem;
            color: #666;
        }}
        
        .summary-card .amount {{
            font-size: 1.1rem;
            font-weight: bold;
            color: #444;
            margin-top: 0.25rem;
        }}
        
        .summary-section {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }}
        
        .summary-section h2 {{
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
        }}
        
        .summary-content {{
            display: flex;
            flex-direction: column;
            gap: 2rem;
            align-items: center;
        }}
        
        .summary-cards {{
            width: 100%;
        }}
        
        .summary-grid {{
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        .chart-container {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}
        
        .chart-container h2 {{
            margin-bottom: 1rem;
        }}
        
        .chart-container img {{
            max-width: 70%;
            height: auto;
        }}
        
        .table-section {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .table-header {{
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .controls {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        
        .filter-group {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .filter-btn {{
            padding: 0.5rem 1rem;
            border: 2px solid #dee2e6;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .filter-btn.active {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}
        
        .pagination {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 1rem 0.5rem 1.5rem 0.5rem;
            padding: 0.5rem;
        }}
        
        .page-info {{
            color: #666;
        }}
        
        .page-controls button {{
            padding: 0.5rem 1rem;
            border: 1px solid #dee2e6;
            background: white;
            cursor: pointer;
            margin: 0 0.25rem;
            border-radius: 4px;
        }}
        
        .page-controls button:hover {{
            background: #f8f9fa;
        }}
        
        .page-controls button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 0.75rem;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        td {{
            padding: 0.5rem 0.75rem;
            border-bottom: 1px solid #dee2e6;
            font-size: 0.9rem;
        }}
        
        .table-row:hover {{
            background-color: #f8f9fa;
        }}
        
        .status-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .status-badge.balanced {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-badge.overpaid {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .status-badge.underpaid {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .hidden {{
            display: none !important;
        }}
        
        /* Responsive design for smaller screens */
        @media (max-width: 768px) {{
            .summary-content {{
                gap: 1rem;
            }}
            
            .container {{
                padding: 10px;
            }}
            
            .summary-grid {{
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 0.5rem;
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🏥 Insurance Reconciliation Report</h1>
            <p>Comprehensive analysis of claims vs invoice transactions with detailed reconciliation status breakdown</p>
        </div>
        
        <!-- Unified Summary and Chart Section -->
        {summary_section}
        
        <!-- Detailed Table -->
        <div class="table-section">
            <div class="table-header">
                <h2>📋 Detailed Claims Data</h2>
                <div class="controls">
                    <div class="filter-group">
                        <label>Filter by Status:</label>
                        <button class="filter-btn active" data-filter="all">All ({analysis_data['total_claims']})</button>
                        <button class="filter-btn" data-filter="BALANCED">Balanced ({analysis_data['balanced']['count']})</button>
                        <button class="filter-btn" data-filter="OVERPAID">Overpaid ({analysis_data['overpaid']['count']})</button>
                        <button class="filter-btn" data-filter="UNDERPAID">Underpaid ({analysis_data['underpaid']['count']})</button>
                    </div>
                </div>
            </div>
            
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Claim ID</th>
                            <th>Patient ID</th>
                            <th>Charges Amount</th>
                            <th>Benefit Amount</th>
                            <th>Transaction Total</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        {table_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="pagination">
                <div class="page-info" id="page-info"></div>
                <div class="page-controls">
                    <button id="prev-btn" onclick="changePage(-1)">« Previous</button>
                    <span id="page-numbers"></span>
                    <button id="next-btn" onclick="changePage(1)">Next »</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Pagination and filtering logic
        let currentPage = 1;
        let rowsPerPage = 20;
        let currentFilter = 'all';
        
        function filterTable(status) {{
            currentFilter = status;
            currentPage = 1;
            
            // Update filter buttons
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.querySelector(`[data-filter="${{status}}"]`).classList.add('active');
            
            // Show/hide rows
            const rows = document.querySelectorAll('.table-row');
            rows.forEach(row => {{
                if (status === 'all' || row.dataset.status === status) {{
                    row.classList.remove('hidden');
                }} else {{
                    row.classList.add('hidden');
                }}
            }});
            
            updatePagination();
        }}
        
        function updatePagination() {{
            const visibleRows = document.querySelectorAll('.table-row:not(.hidden)');
            const totalRows = visibleRows.length;
            const totalPages = Math.ceil(totalRows / rowsPerPage);
            
            // Hide all rows first
            visibleRows.forEach(row => row.style.display = 'none');
            
            // Show current page rows
            const startIndex = (currentPage - 1) * rowsPerPage;
            const endIndex = startIndex + rowsPerPage;
            
            for (let i = startIndex; i < endIndex && i < totalRows; i++) {{
                if (visibleRows[i]) {{
                    visibleRows[i].style.display = '';
                }}
            }}
            
            // Update pagination info
            document.getElementById('page-info').textContent = 
                `Showing ${{startIndex + 1}}-${{Math.min(endIndex, totalRows)}} of ${{totalRows}} records`;
            
            // Update pagination buttons
            document.getElementById('prev-btn').disabled = currentPage === 1;
            document.getElementById('next-btn').disabled = currentPage === totalPages || totalPages === 0;
            
            // Update page numbers
            const pageNumbers = document.getElementById('page-numbers');
            pageNumbers.innerHTML = '';
            
            for (let i = 1; i <= totalPages; i++) {{
                if (i === currentPage || i === 1 || i === totalPages || 
                    (i >= currentPage - 1 && i <= currentPage + 1)) {{
                    const btn = document.createElement('button');
                    btn.textContent = i;
                    btn.onclick = () => {{ currentPage = i; updatePagination(); }};
                    if (i === currentPage) {{
                        btn.style.background = '#007bff';
                        btn.style.color = 'white';
                    }}
                    pageNumbers.appendChild(btn);
                }} else if ((i === currentPage - 2 || i === currentPage + 2) && totalPages > 5) {{
                    const span = document.createElement('span');
                    span.textContent = '...';
                    span.style.padding = '0.5rem';
                    pageNumbers.appendChild(span);
                }}
            }}
        }}
        
        function changePage(direction) {{
            const visibleRows = document.querySelectorAll('.table-row:not(.hidden)');
            const totalPages = Math.ceil(visibleRows.length / rowsPerPage);
            
            currentPage += direction;
            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages) currentPage = totalPages;
            
            updatePagination();
        }}
        
        // Add filter button event listeners
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterTable(btn.dataset.filter);
            }});
        }});
        
        // Initialize pagination
        updatePagination();
    </script>
</body>
</html>
    """

    return html_content


def generate_report(
    reconciled_df: pl.DataFrame, analysis_data: dict, output_file_path: str
) -> str:
    project_root = get_project_root()
    absolute_output_path = os.path.join(project_root, output_file_path)
    ensure_directory_exists(absolute_output_path)

    chart_image = create_pie_chart(analysis_data)
    html_content = generate_html_report(reconciled_df, analysis_data, chart_image)

    with open(absolute_output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return absolute_output_path
