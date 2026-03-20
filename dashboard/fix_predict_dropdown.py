import os

file_path = r'C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static\predict.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Model Dropdown
# It starts with <div class="space-y-4 col-span-1 md:col-span-2">
# and ends with </select>\n                </label>\n            </div>
start_str = '<div class="space-y-4 col-span-1 md:col-span-2">'
end_str = '</select>\n                </label>\n            </div>'

st = text.find(start_str)
end = text.find(end_str)

if st != -1 and end != -1:
    old_dropdown = text[st:end + len(end_str)]
    text = text.replace(old_dropdown, '')

# 2. Update JS to hardcode XGBoost in the payload instead of reading from dropdown
js_st = text.find('model_type: document.getElementById(\'p_model_type\').value,')
if js_st != -1:
    text = text.replace('model_type: document.getElementById(\'p_model_type\').value,', 'model_type: \'xgb\',')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully removed model dropdown from predict.html and set default to XGBoost.')
