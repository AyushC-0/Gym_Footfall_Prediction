import os

file_path = r'C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix Start Prediction Button
old_btn = '<button class="group flex min-w-[200px] cursor-pointer items-center justify-center gap-2 rounded-lg h-14 px-8 bg-primary text-white text-lg font-bold hover:scale-105 transition-all shadow-lg shadow-primary/20">\n<span>Start Prediction</span>'
new_btn = '<button onclick="window.location.href=\'/predict\'" class="group flex min-w-[200px] cursor-pointer items-center justify-center gap-2 rounded-lg h-14 px-8 bg-primary text-white text-lg font-bold hover:scale-105 transition-all shadow-lg shadow-primary/20">\n<span>Start Prediction</span>'

text = text.replace(old_btn, new_btn)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed Start Prediction button in index.html.')
