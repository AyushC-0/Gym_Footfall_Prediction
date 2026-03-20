import os

file_path = r'C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static\predict.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()


# Add IDs to the inputs
text = text.replace('<select class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary"><option>January</option>', '<select id="w_month" onchange="generateWeeklyForecast()" class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary"><option>January</option>')
text = text.replace('<select class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary">\n<option>1st Week</option>', '<select id="w_week" onchange="generateWeeklyForecast()" class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary">\n<option>1st Week</option>')

text = text.replace('<input class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary" type="number" value="1500"/>', '<input id="w_pop" oninput="generateWeeklyForecast()" class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary" type="number" value="1500"/>')


# Update the container
old_container = '''<div class="relative h-64 w-full bg-slate-50 dark:bg-slate-950/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800 flex flex-col items-center justify-center overflow-hidden">
<div class="absolute inset-0 opacity-20 pointer-events-none">
<div class="w-full h-full" style="background-image: linear-gradient(to right, #334155 1px, transparent 1px), linear-gradient(to bottom, #334155 1px, transparent 1px); background-size: 40px 40px;"></div>
</div>
<span class="material-symbols-outlined text-4xl text-slate-400 mb-2" style="">bar_chart</span>
<p class="text-slate-500 font-medium" style="">Weekly Forecast Visualization Placeholder</p>
<p class="text-xs text-slate-400 mt-1 uppercase tracking-widest font-bold" style="">Awaiting Model Input</p>
</div>'''

new_container = '''<div id="weekly_chart_container" class="relative h-64 w-full bg-slate-50 dark:bg-slate-950/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800 flex items-end justify-between px-4 pt-12 pb-8 overflow-hidden">
<div class="absolute inset-0 opacity-20 pointer-events-none z-0">
<div class="w-full h-full" style="background-image: linear-gradient(to right, #334155 1px, transparent 1px), linear-gradient(to bottom, #334155 1px, transparent 1px); background-size: 40px 40px;"></div>
</div>
<div class="absolute inset-0 flex flex-col items-center justify-center z-10" id="weekly_chart_placeholder">
    <span class="material-symbols-outlined text-4xl text-slate-400 mb-2">bar_chart</span>
    <p class="text-slate-500 font-medium">Weekly Forecast Visualization Placeholder</p>
    <p class="text-xs text-slate-400 mt-1 uppercase tracking-widest font-bold">Adjust parameters to forecast</p>
</div>
</div>'''

text = text.replace(old_container, new_container)


# Add JS function
js_code = '''
async function generateWeeklyForecast() {
    const payload = {
        model_type: 'xgb',
        month: document.getElementById('w_month').value,
        week: document.getElementById('w_week').value,
        base_pop: parseInt(document.getElementById('w_pop').value) || 1500
    };

    try {
        const response = await fetch('/api/weekly_forecast', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        
        let container = document.getElementById('weekly_chart_container');
        let placeholder = document.getElementById('weekly_chart_placeholder');
        if (placeholder) placeholder.style.display = 'none';
        
        // Remove existing bars
        container.querySelectorAll('.forecast-bar').forEach(el => el.remove());
        
        // Find max prediction for scaling
        let maxPred = Math.max(...data.forecasts.map(d => d.prediction), 10);
        
        data.forecasts.forEach(item => {
            let heightPct = Math.max((item.prediction / maxPred) * 100, 5); // min 5% height
            
            let colorClass = 'bg-primary/80';
            if (item.prediction > 120) colorClass = 'bg-red-500/80';
            else if (item.prediction > 60) colorClass = 'bg-yellow-500/80';
            if (item.prediction === 0) colorClass = 'bg-slate-300 dark:bg-slate-700'; // closed
            
            let col = document.createElement('div');
            col.className = 'forecast-bar flex flex-col items-center w-full z-10 mx-1 group cursor-help transition-all duration-500 h-full justify-end';
            
            col.innerHTML = `
                <div class="relative w-full \${colorClass} rounded-t-md hover:brightness-110 transition-all duration-300" style="height: \${heightPct}%;">
                    <div class="absolute -top-10 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-white px-2 py-1 rounded text-xs whitespace-nowrap shadow-lg z-20 pointer-events-none">
                        \${item.prediction} people
                    </div>
                </div>
                <span class="text-[10px] sm:text-xs font-bold text-slate-500 uppercase mt-2 text-center w-full truncate">\${item.day.substring(0,3)}</span>
            `;
            container.appendChild(col);
        });
        
    } catch(err) {
        console.error("Weekly forecast error:", err);
    }
}

// Automatically generate forecast on load for the default values
document.addEventListener("DOMContentLoaded", () => {
    generateWeeklyForecast();
});
'''

text = text.replace('</script>', js_code + '\n</script>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Added weekly forecast JS and HTML to predict.html')
