import os

file_path = r'C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static\compare.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Change grid
text = text.replace('<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">', '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">')

# XGBoost Card HTML
xgb_card = '''
    <div class="bg-white dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-800 p-8 flex flex-col gap-6 shadow-sm">
        <div class="flex justify-between items-start">
            <div>
                <span class="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-500 text-xs font-bold uppercase tracking-wider">Fast & Accurate</span>
                <h3 class="text-2xl font-bold mt-2">XGBoost</h3>
            </div>
            <div class="text-right">
                <p class="text-3xl font-black text-indigo-500">0.90</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 font-bold">R-SQUARED</p>
            </div>
        </div>
        <!-- Bar Chart Accuracy Visualization -->
        <div class="space-y-4">
            <p class="text-sm font-semibold text-slate-500">Feature Importance Weight</p>
            <div class="space-y-3">
                <div>
                    <div class="flex justify-between text-xs mb-1"><span>Historical Data</span><span>82%</span></div>
                    <div class="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div class="bg-indigo-500 h-full w-[82%] rounded-full"></div>
                    </div>
                </div>
                <div>
                    <div class="flex justify-between text-xs mb-1"><span>Time of Day</span><span>68%</span></div>
                    <div class="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div class="bg-indigo-500/70 h-full w-[68%] rounded-full"></div>
                    </div>
                </div>
            </div>
        </div>
        <!-- Pros/Cons -->
        <div class="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200 dark:border-slate-800">
            <div>
                <h4 class="text-xs font-bold text-slate-400 uppercase mb-2">Pros</h4>
                <ul class="text-sm space-y-1 text-slate-600 dark:text-slate-300">
                    <li class="flex items-center gap-1"><span class="material-symbols-outlined text-green-500 text-sm">check_circle</span> Fast performance</li>
                    <li class="flex items-center gap-1"><span class="material-symbols-outlined text-green-500 text-sm">check_circle</span> Gradient boosting</li>
                </ul>
            </div>
            <div>
                <h4 class="text-xs font-bold text-slate-400 uppercase mb-2">Cons</h4>
                <ul class="text-sm space-y-1 text-slate-600 dark:text-slate-300">
                    <li class="flex items-center gap-1"><span class="material-symbols-outlined text-amber-500 text-sm">error</span> Potential Overfit</li>
                    <li class="flex items-center gap-1"><span class="material-symbols-outlined text-amber-500 text-sm">error</span> Hard validation</li>
                </ul>
            </div>
        </div>
    </div>
'''

# Insert after Random Forest Card, before Linear Regression card.
# I will find the end of the RF card and insert it there.
rf_end_index = text.find('<!-- Linear Regression Card -->')
if rf_end_index != -1:
    text = text[:rf_end_index] + xgb_card + '\n' + text[rf_end_index:]

# Add XGBoost to the chart legend
chart_legend = '''
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-primary"></div>
                    <span class="text-xs font-medium">Random Forest</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-indigo-500"></div>
                    <span class="text-xs font-medium">XGBoost</span>
                </div>
'''
text = text.replace('''<div class="flex items-center gap-2">
<div class="w-3 h-3 rounded-full bg-primary"></div>
<span class="text-xs font-medium">Random Forest</span>
</div>''', chart_legend)

# Add XGBoost line to SVG
xgb_path = '''
    <!-- XGB Predicted Path (Indigo) -->
    <path d="M0,158 L100,123 L200,140 L300,82 L400,95 L500,68 L600,90 L700,58 L800,72" fill="none" stroke="#6366f1" stroke-linecap="round" stroke-width="3"></path>
'''
text = text.replace('<!-- RF Predicted Path (Primary) -->', xgb_path + '<!-- RF Predicted Path (Primary) -->')

# Recommendation text update
text = text.replace('b>Random Forest</b> model is recommended for all production', 'b>Random Forest</b> and <b>XGBoost</b> models are highly recommended for all production')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Modified compare.html successfully.")
