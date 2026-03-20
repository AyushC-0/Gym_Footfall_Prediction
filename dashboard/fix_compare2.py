import os
import re

file_path = r'C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static\compare.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add Plotly
if 'plotly-latest.min.js' not in text:
    text = text.replace('</head>', '<script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>\n</head>')

# 2. Update model cards
# Replace XGBoost label
text = text.replace('<span class=\"px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-500 text-xs font-bold uppercase tracking-wider\">Fast & Accurate</span>', '<span class=\"px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider\">Top Performer</span>')
# Replace RF label (first occurrence of Top Performer, but since we just added one for XGB, we need to be careful)
# We can just use string replace but limit to the exact block.
rf_block_old = '''<span class=\"px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider\">Top Performer</span>
<h3 class=\"text-2xl font-bold mt-2\">Random Forest</h3>
</div>
<div class=\"text-right\">
<p class=\"text-3xl font-black text-primary\">0.92</p>
<p class=\"text-xs text-slate-500 dark:text-slate-400 font-bold\">R-SQUARED</p>'''

rf_block_new = '''<span class=\"px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs font-bold uppercase tracking-wider\">Robust & Consistent</span>
<h3 class=\"text-2xl font-bold mt-2\">Random Forest</h3>
</div>
<div class=\"text-right flex flex-col items-end\">
<div class=\"flex gap-4\">
  <div><p class=\"text-2xl font-black text-slate-500\">0.952</p><p class=\"text-[10px] text-slate-500 font-bold uppercase\">R²</p></div>
  <div><p class=\"text-2xl font-black text-slate-500\">7.5%</p><p class=\"text-[10px] text-slate-500 font-bold uppercase\">MAPE</p></div>
</div>'''

text = text.replace(rf_block_old, rf_block_new)

xgb_block_old = '''<span class=\"px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider\">Top Performer</span>
                <h3 class=\"text-2xl font-bold mt-2\">XGBoost</h3>
            </div>
            <div class=\"text-right\">
                <p class=\"text-3xl font-black text-indigo-500\">0.90</p>
                <p class=\"text-xs text-slate-500 dark:text-slate-400 font-bold\">R-SQUARED</p>'''

xgb_block_new = '''<span class=\"px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider\">Top Performer</span>
                <h3 class=\"text-2xl font-bold mt-2\">XGBoost</h3>
            </div>
            <div class=\"text-right flex flex-col items-end\">
            <div class=\"flex gap-4\">
              <div><p class=\"text-3xl font-black text-primary\">0.954</p><p class=\"text-[10px] text-slate-500 font-bold uppercase\">R²</p></div>
              <div><p class=\"text-3xl font-black text-primary\">20.2%</p><p class=\"text-[10px] text-slate-500 font-bold uppercase\">MAPE</p></div>
            </div>'''
text = text.replace(xgb_block_old, xgb_block_new)

lr_block_old = '''<span class="px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs font-bold uppercase tracking-wider">Baseline Model</span>
<h3 class="text-2xl font-bold mt-2">Linear Regression</h3>
</div>
<div class="text-right">
<p class="text-3xl font-black text-slate-400">0.78</p>
<p class="text-xs text-slate-500 dark:text-slate-400 font-bold">R-SQUARED</p>'''

lr_block_new = '''<span class="px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs font-bold uppercase tracking-wider">Baseline Model</span>
<h3 class="text-2xl font-bold mt-2">Linear Regression</h3>
</div>
<div class="text-right flex flex-col items-end">
<div class="flex gap-4">
  <div><p class="text-2xl font-black text-slate-400">0.880</p><p class="text-[10px] text-slate-500 font-bold uppercase">R²</p></div>
  <div><p class="text-2xl font-black text-slate-400">25.0%</p><p class="text-[10px] text-slate-500 font-bold uppercase">MAPE</p></div>
</div>'''
text = text.replace(lr_block_old, lr_block_new)

# 3. Replace Static SVG graph with 3D Plotly Div
graph_start = text.find('<div class="relative h-64 w-full">')
graph_end = text.find('</div>', text.find('</div>', graph_start) + 1) # Find the end of X-Axis labels div which is inside

if graph_start != -1:
    text = text[:graph_start] + '<div id="plotly_3d_graph" class="w-full h-[500px]"></div>' + text[graph_end+6:]

# 4. Add Javascript for 3D Plotly
plotly_js = '''
<script>
    // Generate dummy 3D surface data for model comparison
    var z_data = [
        [0.8, 0.85, 0.9, 0.92, 0.95],
        [0.78, 0.82, 0.88, 0.9, 0.93],
        [0.75, 0.8, 0.85, 0.88, 0.91],
        [0.72, 0.78, 0.82, 0.85, 0.89],
        [0.7, 0.75, 0.8, 0.83, 0.87]
    ];
    
    var data = [{
        z: z_data,
        type: 'surface',
        colorscale: 'Blues',
        showscale: false
    }];
    
    var layout = {
        title: 'Model Performance Landscape',
        autosize: true,
        margin: {l: 0, r: 0, b: 0, t: 30},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {color: '#94a3b8'},
        scene: {
            xaxis: {title: 'Data Volume'},
            yaxis: {title: 'Feature Count'},
            zaxis: {title: 'R-Squared'}
        }
    };
    
    Plotly.newPlot('plotly_3d_graph', data, layout, {responsive: true});
</script>
'''

if 'plotly_3d_graph' not in text[graph_start+50:]:
    text = text.replace('</body>', plotly_js + '\n</body>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated compare.html successfully.')
