# -*- coding: utf-8 -*-
import zipfile, plistlib, os, shutil
from PIL import Image

def generate_app_icons(source_icon, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(source_icon)
    
    icon_sizes = {
        'AppIcon60x60@2x.png': (120, 120),
        'AppIcon60x60@3x.png': (180, 180),
        'AppIcon76x76@2x~ipad.png': (152, 152),
        'AppIcon83.5x83.5@2x~ipad.png': (167, 167),
        'AppIcon20x20@2x.png': (40, 40),
        'AppIcon20x20@3x.png': (60, 60),
        'AppIcon29x29@2x.png': (58, 58),
        'AppIcon29x29@3x.png': (87, 87),
        'AppIcon40x40@2x.png': (80, 80),
        'AppIcon40x40@3x.png': (120, 120),
    }
    
    generated = {}
    for filename, size in icon_sizes.items():
        resized = img.resize(size, Image.Resampling.LANCZOS)
        path = os.path.join(output_dir, filename)
        resized.save(path, 'PNG')
        with open(path, 'rb') as f:
            generated[filename] = f.read()
    return generated

def clean_strings(content):
    replacements = [
        ('RyukGram', 'Lucid Insta'),
        ('ryukgram', 'lucid_insta'),
        ('SCInsta', 'Lucid Suite'),
        ('scinsta', 'lucid_suite'),
        ('BHInstagram', 'Lucid Suite'),
        ('bhinstagram', 'lucid_suite'),
        ('faroukbmiled', 'vicrtzx'),
        ('BandarHL', 'vicrtzx'),
        ('SoCuul', 'vicrtzx'),
        ('Donate to Ryuk', 'Lucid Insta'),
        ('Doe para Ryuk', 'Lucid Insta'),
        ('Support Lucid Insta development', 'Lucid Insta'),
        ('Apoie o desenvolvimento do Lucid Insta', 'Lucid Insta'),
        ('Lucid Insta developer', 'Autor'),
        ('Desenvolvedor Lucid Insta', 'vicrtzx'),
        ('SCInsta developer', 'Lucid Suite'),
        ('Desenvolvedor do SCInsta', 'Lucid Suite'),
        ('BHInstagram developer', 'Lucid Suite'),
        ('Desenvolvedor do BHInstagram', 'Lucid Suite'),
        ('Credits', 'Sobre o Lucid'),
        ('Créditos', 'Sobre o Lucid'),
        ('Developers', 'Autor'),
        ('Desenvolvedores', 'Autor'),
        ('Join Telegram channel', 'Lucid Insta'),
        ('Junte-se ao canal Telegram', 'Lucid Insta'),
        ('View on GitHub', 'Lucid Insta'),
        ('Ver no GitHub', 'Lucid Insta'),
        ('Open GitHub', 'Lucid Insta'),
        ('Abra o GitHub', 'Lucid Insta'),
        ('Donate', 'Lucid'),
        ('Doar', 'Lucid'),
        ('Telegram channel', 'Lucid Insta'),
        ('Canal de telegrama', 'Lucid Insta'),
        ('Version, credits, and links', 'Versão e detalhes'),
        ('Versão, créditos e links', 'Versão e detalhes'),
        ('Lucid Insta is an independent project inspired by SCInsta.', 'Lucid Insta — Projeto Pessoal & Autoral.'),
        ('O Lucid Insta é um projeto independente inspirado no SCInsta.', 'Lucid Insta — Projeto Pessoal & Autoral.'),
        ('Appreciate the support', 'Versão Autoral'),
        ('Obrigado pelo apoio', 'Versão Autoral'),
    ]
    for old, new in replacements:
        content = content.replace(old, new)
    return content

def patch_bundle_strings(bundle_dir):
    if not os.path.exists(bundle_dir):
        return
        
    for root, dirs, files in os.walk(bundle_dir):
        for file in files:
            if file == 'Localizable.strings':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    cleaned = clean_strings(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned)
                    print(f"Purged third-party credits and branded {file_path}")
                except Exception as e:
                    print(f"Error patching {file_path}: {e}")

def patch_base_ipa():
    input_ipa = 'packages/com.burbn.instagram.ipa'
    if not os.path.exists(input_ipa):
        input_ipa = 'com.burbn.instagram.ipa'
        
    output_ipa = 'packages/BaseInstagram-branded.ipa'
    os.makedirs('packages', exist_ok=True)
    
    print(f"Preparing Liquid Glass icons...")
    icon_map = generate_app_icons('AppIcon1024.png', 'temp_icons')
    
    print(f"Branding {input_ipa} -> {output_ipa}...")
    with zipfile.ZipFile(input_ipa, 'r') as zin, zipfile.ZipFile(output_ipa, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            filename = item.filename
            
            # 1. Update Info.plist
            if filename.endswith('.app/Info.plist') and 'Payload/' in filename and not 'PlugIns/' in filename:
                data = zin.read(filename)
                pl = plistlib.loads(data)
                pl['CFBundleDisplayName'] = 'Lucid Insta'
                pl['CFBundleName'] = 'Lucid Insta'
                new_data = plistlib.dumps(pl, fmt=plistlib.FMT_XML)
                zout.writestr(item, new_data)
                print(f"Patched {filename} -> DisplayName: Lucid Insta")
                
            # 2. Replace App Icons
            elif any(filename.endswith('/' + k) for k in icon_map):
                base_k = os.path.basename(filename)
                zout.writestr(item, icon_map[base_k])
                print(f"Replaced {filename} with Liquid Glass icon")
                
            else:
                zout.writestr(item, zin.read(filename))

    print(f"Base IPA branded successfully!")

if __name__ == '__main__':
    patch_bundle_strings('packages/RyukGram.bundle')
    patch_base_ipa()
