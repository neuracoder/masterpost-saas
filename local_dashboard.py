import subprocess
import json
import webbrowser
import os
import sys
from datetime import datetime

# Configuration
SERVER_IP = "49.13.145.150"
SERVER_USER = "root"
REMOTE_PATH = "/root/masterpost-saas/backend/admin_api.py"
OUTPUT_FILE = "admin_dashboard.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Masterpost Admin - User Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 text-gray-900">
    <div class="min-h-screen p-6">
        
        <!-- Header & KPI Mini Row -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
            <div>
                <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
                <p class="text-sm text-gray-500">Updated: <span id="gen-time"></span></p>
            </div>
            
            <!-- Mini Cards -->
            <div class="grid grid-cols-4 gap-4 w-full md:w-auto">
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-100">
                    <div class="text-xs text-gray-500 uppercase tracking-wide">Total Users</div>
                    <div class="font-bold text-lg" id="total-users">-</div>
                </div>
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-100 border-l-4 border-l-green-500">
                    <div class="text-xs text-gray-500 uppercase tracking-wide">Paid Users</div>
                    <div class="font-bold text-lg text-green-700" id="paid-users">-</div>
                </div>
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-100">
                    <div class="text-xs text-gray-500 uppercase tracking-wide">Free Users</div>
                    <div class="font-bold text-lg text-gray-600" id="free-users">-</div>
                </div>
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-100">
                    <div class="text-xs text-gray-500 uppercase tracking-wide">Total Revenue</div>
                    <div class="font-bold text-lg text-emerald-600" id="revenue">-</div>
                </div>
            </div>
        </div>

        <!-- Main User Table -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                    <thead class="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
                        <tr>
                            <th class="px-6 py-3 w-1/4">User Info</th>
                            <th class="px-6 py-3 w-32 text-center">Plan Status</th>
                            <th class="px-6 py-3 text-right">Credits</th>
                            <th class="px-6 py-3 text-right">Total Spent</th>
                            <th class="px-6 py-3 w-1/4">Last Purchase</th>
                            <th class="px-6 py-3 text-center">Usage Stats</th>
                            <th class="px-6 py-3 text-right">Last Active</th>
                        </tr>
                    </thead>
                    <tbody id="user-rows" class="divide-y divide-gray-100">
                        <!-- JS GENERATED -->
                    </tbody>
                </table>
            </div>
        </div>
        
    </div>

    <script>
        const data = DATA_PLACEHOLDER;
        const fmtMoney = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

        // Header Stats
        document.getElementById('gen-time').textContent = new Date(data.generated_at).toLocaleString();
        document.getElementById('total-users').textContent = data.summary.total_users;
        document.getElementById('paid-users').textContent = data.summary.paid_users;
        document.getElementById('free-users').textContent = data.summary.free_users;
        document.getElementById('revenue').textContent = fmtMoney.format(data.summary.total_revenue);

        // Table Rows
        const tbody = document.getElementById('user-rows');
        
        data.users_list.forEach(u => {
            const isPaid = u.is_paid;
            const statusBadge = isPaid 
                ? `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200"><i class="fas fa-crown mr-1"></i> PRO</span>`
                : `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">FREE</span>`;
            
            const lastPack = u.last_pack ? `<div class="text-xs font-semibold text-emerald-600">${u.last_pack}</div>` : '<span class="text-xs text-gray-400">-</span>';
            const purchaseInfo = u.last_purchase_date 
                ? `<div>${lastPack}<div class="text-[10px] text-gray-400">${new Date(u.last_purchase_date).toLocaleDateString()}</div></div>`
                : '<span class="text-xs text-gray-400">Never</span>';

            const activeDate = new Date(u.last_active);
            const now = new Date();
            const diffDays = Math.floor((now - activeDate) / (1000 * 60 * 60 * 24));
            let activeColor = 'text-green-600';
            if(diffDays > 7) activeColor = 'text-yellow-600';
            if(diffDays > 30) activeColor = 'text-gray-400';

            const row = `
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4">
                        <div class="font-medium text-gray-900">${u.email}</div>
                        <div class="text-xs text-gray-400">Joined ${new Date(u.created_at).toLocaleDateString()}</div>
                    </td>
                    <td class="px-6 py-4 text-center">
                        ${statusBadge}
                    </td>
                    <td class="px-6 py-4 text-right font-mono font-bold text-gray-700">
                        ${u.credits.toLocaleString()}
                    </td>
                     <td class="px-6 py-4 text-right font-medium text-gray-900">
                        ${fmtMoney.format(u.total_spent)}
                    </td>
                    <td class="px-6 py-4">
                        ${purchaseInfo}
                    </td>
                    <td class="px-6 py-4 text-center">
                        <div class="flex justify-center space-x-2 text-xs">
                            <span class="bg-blue-50 text-blue-700 px-2 py-1 rounded" title="Basic Images">B: ${u.usage_basic}</span>
                            <span class="bg-purple-50 text-purple-700 px-2 py-1 rounded" title="Premium/Qwen Images">P: ${u.usage_premium}</span>
                        </div>
                    </td>
                    <td class="px-6 py-4 text-right text-xs ${activeColor} font-medium">
                        ${diffDays === 0 ? 'Today' : diffDays + ' days ago'}
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    </script>
</body>
</html>
"""

def main():
    print(f"Connecting to {SERVER_IP}...")
    try:
        cmd = ["ssh", f"{SERVER_USER}@{SERVER_IP}", f"python3 {REMOTE_PATH}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error connecting to server:", result.stderr)
            return

        output = result.stdout
        json_start = output.find('{')
        if json_start == -1: raise ValueError("No JSON found")
        
        data = json.loads(output[json_start:])
        
        if "error" in data:
            print(f"Error: {data['error']}")
            return

        html_content = HTML_TEMPLATE.replace("DATA_PLACEHOLDER", json.dumps(data))
        output_path = os.path.abspath(OUTPUT_FILE)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"Dashboard updated: {output_path}")
        webbrowser.open(f"file://{output_path}")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()
