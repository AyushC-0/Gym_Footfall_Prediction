import os
import shutil

source_dir = r"C:\Users\Ayush Choudhury\Desktop\stitch_wegogym_home\stitch_wegogym_home"
dest_dir = r"C:\Users\Ayush Choudhury\Documents\GitHub\Gym_Footfall_Prediction\dashboard\static"
os.makedirs(dest_dir, exist_ok=True)

files = [
    (r"wegogym_home\code.html", "index.html"),
    (r"wegogym_prediction_engine_updated\code.html", "predict.html"),
    (r"wegogym_model_comparison\code.html", "compare.html"),
    (r"wegogym_project_overview\code.html", "overview.html")
]

for src, dst in files:
    with open(os.path.join(source_dir, src), 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update navigation links
    content = content.replace('href="#" style="">Home', 'href="/" style="">Home') \
                     .replace('href="#" style="">Prediction Engine', 'href="/predict" style="">Prediction Engine') \
                     .replace('href="#" style="">Model Comparison', 'href="/compare" style="">Model Comparison') \
                     .replace('href="#" style="">Project Overview', 'href="/overview" style="">Project Overview')

    # Catch cases without the style="" attribute
    content = content.replace('href="#">Home', 'href="/">Home') \
                     .replace('href="#">Prediction Engine', 'href="/predict">Prediction Engine') \
                     .replace('href="#">Model Comparison', 'href="/compare">Model Comparison') \
                     .replace('href="#">Project Overview', 'href="/overview">Project Overview')
                     
    with open(os.path.join(dest_dir, dst), 'w', encoding='utf-8') as f:
        f.write(content)

print('Copied and modified HTML files.')
