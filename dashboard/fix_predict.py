import os

file_path = r'C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static\predict.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Enlarge the circle and remove the tabs below it
st = text.find('<div class="size-40 rounded-full border-[10px]')
end_str = '<div class="w-full grid grid-cols-3 gap-2">'
end = text.find(end_str, st)
# find the ending div of the grid
end = text.find('</div>\n</div>\n</div>', end)

if st != -1 and end != -1:
    old_section = text[st:end+12]
    
    new_circle = '''<div class="size-56 rounded-full border-[12px] border-red-500/20 flex flex-col items-center justify-center relative mb-6 shadow-[0_0_30px_rgba(239,68,68,0.2)] transition-all duration-500" id="status_circle_container">
<div class="absolute inset-0 rounded-full border-[12px] border-red-500 border-t-transparent border-l-transparent rotate-45 transition-all duration-1000" id="status_circle_ring"></div>
<span id="out_status" class="text-5xl font-black text-red-500 transition-colors duration-500" style="">HIGH</span>
<span class="text-sm font-bold text-slate-500 mt-1" style="">CONGESTION</span>
</div>
<h3 id="out_val" class="text-2xl font-bold mb-3" style="">Estimated Footfall: 420</h3>
<p id="out_desc" class="text-base text-slate-500 mb-2 px-4" style="">Based on current parameters, the gym is expected to reach near-peak capacity. Consider staffing increases.</p>'''

    text = text.replace(old_section, new_circle)


# Fix the JS
js_st = text.find('outStatus.parentElement.className')
js_end = text.find('`;\n        \n    } catch', js_st)

if js_st != -1 and js_end != -1:
    old_js = text[js_st:js_end+2]
    new_js = '''const circleContainer = document.getElementById('status_circle_container');
        const circleRing = document.getElementById('status_circle_ring');
        
        let shadowColor = '34,197,94'; // green
        if (status === 'HIGH') shadowColor = '239,68,68'; // red
        else if (status === 'MED') shadowColor = '234,179,8'; // yellow
        
        circleContainer.className = `size-56 rounded-full border-[12px] ${borderClass}/20 flex flex-col items-center justify-center relative mb-6 shadow-[0_0_30px_rgba(${shadowColor},0.2)] transition-all duration-500`;
        circleRing.className = `absolute inset-0 rounded-full border-[12px] ${borderClass} border-t-transparent border-l-transparent rotate-45 transition-all duration-1000`;
        outStatus.className = `text-5xl font-black ${colorClass} transition-colors duration-500`;'''
    text = text.replace(old_js, new_js)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Modified predict.html layout successfully.')
