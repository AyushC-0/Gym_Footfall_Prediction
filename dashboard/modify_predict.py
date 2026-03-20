import os

file_path = r'C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static\predict.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add Model selector
model_html = '''
            <div class="space-y-4 col-span-1 md:col-span-2">
                <label class="block" style="">
                    <span class="text-sm font-semibold mb-2 block" style="">AI Model</span>
                    <select id="p_model_type" class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary">
                        <option value="rf">Random Forest (Recommended)</option>
                        <option value="xgb">XGBoost</option>
                        <option value="baseline">Linear Regression (Baseline)</option>
                    </select>
                </label>
            </div>
'''
text = text.replace('<div class="grid grid-cols-1 md:grid-cols-2 gap-6">', '<div class="grid grid-cols-1 md:grid-cols-2 gap-6">\n' + model_html)

# Add IDs to elements
text = text.replace('<select class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary">\n<option>Monday</option>', '<select id="p_day" class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary">\n<option>Monday</option>')
text = text.replace('<select class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary">\n<option>January</option>', '<select id="p_month" class="w-full rounded-lg border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-4 py-3 focus:ring-primary focus:border-primary">\n<option>January</option>')

text = text.replace('<button class="flex flex-col items-center gap-2 p-3 rounded-lg border border-primary bg-primary/10 text-primary" style="">\n<span class="material-symbols-outlined" style="">sunny</span>\n<span class="text-[10px] font-bold uppercase" style="">Normal</span>\n</button>', '<button onclick="setWeather(this, \'normal\')" class="weather-btn active flex flex-col items-center gap-2 p-3 rounded-lg border border-primary bg-primary/10 text-primary" style="">\n<span class="material-symbols-outlined" style="">sunny</span>\n<span class="text-[10px] font-bold uppercase" style="">Normal</span>\n</button>')
text = text.replace('<button class="flex flex-col items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-colors" style="">\n<span class="material-symbols-outlined" style="">rainy</span>\n<span class="text-[10px] font-bold uppercase" style="">Heavy Rain</span>\n</button>', '<button onclick="setWeather(this, \'heavy_rain\')" class="weather-btn flex flex-col items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-colors" style="">\n<span class="material-symbols-outlined" style="">rainy</span>\n<span class="text-[10px] font-bold uppercase" style="">Heavy Rain</span>\n</button>')
text = text.replace('<button class="flex flex-col items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-colors" style="">\n<span class="material-symbols-outlined" style="">thermostat</span>\n<span class="text-[10px] font-bold uppercase" style="">Heat</span>\n</button>', '<button onclick="setWeather(this, \'heat\')" class="weather-btn flex flex-col items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-colors" style="">\n<span class="material-symbols-outlined" style="">thermostat</span>\n<span class="text-[10px] font-bold uppercase" style="">Heat</span>\n</button>')
text = text.replace('<button class="flex flex-col items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-colors" style="">\n<span class="material-symbols-outlined" style="">ac_unit</span>\n<span class="text-[10px] font-bold uppercase" style="">Cold</span>\n</button>', '<button onclick="setWeather(this, \'cold\')" class="weather-btn flex flex-col items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-colors" style="">\n<span class="material-symbols-outlined" style="">ac_unit</span>\n<span class="text-[10px] font-bold uppercase" style="">Cold</span>\n</button>')

text = text.replace('<button class="flex-1 py-2 text-sm font-medium rounded-md bg-white dark:bg-slate-800 shadow-sm" style="">None</button>\n<button class="flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">Midterm</button>\n<button class="flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">Endterm</button>', '<button onclick="setExam(this, \'none\')" class="exam-btn active flex-1 py-2 text-sm font-medium rounded-md bg-white dark:bg-slate-800 shadow-sm text-slate-900 dark:text-white" style="">None</button>\n<button onclick="setExam(this, \'midterm\')" class="exam-btn flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">Midterm</button>\n<button onclick="setExam(this, \'endterm\')" class="exam-btn flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">Endterm</button>')

text = text.replace('<button class="flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">None</button>\n<button class="flex-1 py-2 text-sm font-medium rounded-md bg-white dark:bg-slate-800 shadow-sm" style="">Low</button>\n<button class="flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">Med</button>\n<button class="flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">High</button>', '<button onclick="setMaint(this, \'none\')" class="maint-btn active flex-1 py-2 text-sm font-medium rounded-md bg-white dark:bg-slate-800 shadow-sm text-slate-900 dark:text-white" style="">None</button>\n<button onclick="setMaint(this, \'low\')" class="maint-btn flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">Low</button>\n<button onclick="setMaint(this, \'med\')" class="maint-btn flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">Med</button>\n<button onclick="setMaint(this, \'high\')" class="maint-btn flex-1 py-2 text-sm font-medium rounded-md text-slate-500" style="">High</button>')

text = text.replace('<input class="sr-only peer" type="checkbox" value=""/>', '<input id="p_vacation" class="sr-only peer" type="checkbox" value=""/>')

text = text.replace('<input class="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary" max="5000" min="0" type="range" value="1240"/>', '<input id="p_pop" class="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary" max="5000" min="0" type="range" value="1240" oninput="document.getElementById(\'pop_val\').innerText=this.value"/>')
text = text.replace('<span class="text-primary font-bold" style="">1,240</span>', '<span id="pop_val" class="text-primary font-bold" style="">1240</span>')

text = text.replace('<input class="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary" max="5" min="1" step="1" type="range" value="4"/>', '<input id="p_adopt" class="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary" max="5" min="1" step="1" type="range" value="4" oninput="document.getElementById(\'adopt_val\').innerText=\'Level \'+this.value"/>')
text = text.replace('<span class="text-primary font-bold" style="">Level 4</span>', '<span id="adopt_val" class="text-primary font-bold" style="">Level 4</span>')

text = text.replace('<button class="bg-primary hover:bg-primary/90 text-white px-8 py-3 rounded-lg font-bold transition-all flex items-center gap-2" style="">', '<button onclick="generatePrediction()" class="bg-primary hover:bg-primary/90 text-white px-8 py-3 rounded-lg font-bold transition-all flex items-center gap-2 w-full" style="">')

text = text.replace('<h3 class="text-xl font-bold mb-2" style="">Estimated Footfall: 420</h3>', '<h3 id="out_val" class="text-xl font-bold mb-2" style="">Estimated Footfall: 420</h3>')
text = text.replace('<span class="text-3xl font-black text-red-500" style="">HIGH</span>', '<span id="out_status" class="text-3xl font-black text-red-500" style="">HIGH</span>')
text = text.replace('<p class="text-sm text-slate-500 mb-6 px-4" style="">Based on current parameters, the gym is expected to reach near-peak capacity. Consider staffing increases.</p>', '<p id="out_desc" class="text-sm text-slate-500 mb-6 px-4" style="">Based on current parameters, the gym is expected to reach near-peak capacity. Consider staffing increases.</p>')


js_code = '''
<script>
let currentWeather = 'normal';
let currentExam = 'none';
let currentMaint = 'none';

function setWeather(el, val) {
    document.querySelectorAll('.weather-btn').forEach(btn => {
        btn.className = 'weather-btn flex flex-col items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-colors';
    });
    el.className = 'weather-btn active flex flex-col items-center gap-2 p-3 rounded-lg border border-primary bg-primary/10 text-primary';
    currentWeather = val;
}
function setExam(el, val) {
    document.querySelectorAll('.exam-btn').forEach(btn => {
        btn.className = 'exam-btn flex-1 py-2 text-sm font-medium rounded-md text-slate-500';
    });
    el.className = 'exam-btn active flex-1 py-2 text-sm font-medium rounded-md bg-white dark:bg-slate-800 shadow-sm text-slate-900 dark:text-white';
    currentExam = val;
}
function setMaint(el, val) {
    document.querySelectorAll('.maint-btn').forEach(btn => {
        btn.className = 'maint-btn flex-1 py-2 text-sm font-medium rounded-md text-slate-500';
    });
    el.className = 'maint-btn active flex-1 py-2 text-sm font-medium rounded-md bg-white dark:bg-slate-800 shadow-sm text-slate-900 dark:text-white';
    currentMaint = val;
}

async function generatePrediction() {
    const payload = {
        model_type: document.getElementById('p_model_type').value,
        day: document.getElementById('p_day').value,
        month: document.getElementById('p_month').value,
        year: 2024,
        is_vacation: document.getElementById('p_vacation').checked,
        is_open: true,
        pop: parseInt(document.getElementById('p_pop').value),
        stress: 3,
        adopt: parseInt(document.getElementById('p_adopt').value),
        exam: currentExam,
        weather: currentWeather,
        maint: currentMaint
    };

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        const pred = data.prediction;
        
        document.getElementById('out_val').innerText = 'Estimated Footfall: ' + pred;
        
        let status = 'LOW';
        let colorClass = 'text-green-500';
        let borderClass = 'border-green-500';
        let bgClass = 'bg-green-500/10';
        let desc = 'Comfortable environment. Standard staffing is adequate.';
        
        if (pred > 120) {
            status = 'HIGH';
            colorClass = 'text-red-500';
            borderClass = 'border-red-500';
            bgClass = 'bg-red-500/10';
            desc = 'Reaching near-peak capacity. Consider staffing increases.';
        } else if (pred > 60) {
            status = 'MED';
            colorClass = 'text-yellow-500';
            borderClass = 'border-yellow-500';
            bgClass = 'bg-yellow-500/10';
            desc = 'Moderate footfall expected. Keep standard operations.';
        }
        
        const outStatus = document.getElementById('out_status');
        outStatus.innerText = status;
        outStatus.className = 'text-3xl font-black ' + colorClass;
        document.getElementById('out_desc').innerText = desc;
        
        // Update styling of the circle as well
        outStatus.parentElement.className = `size-40 rounded-full border-[10px] ${borderClass}/20 flex flex-col items-center justify-center relative mb-4`;
        outStatus.parentElement.innerHTML = `
            <div class="absolute inset-0 rounded-full border-[10px] ${borderClass} border-t-transparent border-l-transparent rotate-45"></div>
            <span id="out_status" class="text-3xl font-black ${colorClass}">${status}</span>
            <span class="text-xs font-bold text-slate-500" style="">CONGESTION</span>
        `;
        
    } catch(err) {
        console.error(err);
    }
}
</script>
</body>
'''

text = text.replace('</body>', js_code)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Modified predict.html successfully.")
