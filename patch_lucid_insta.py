# -*- coding: utf-8 -*-
import os
import re
import shutil
import zipfile
import plistlib
from PIL import Image

LUCID_VERSION = "1.2"
LUCID_FOOTER = "Lucid v1.2 • Liquid Glass Edition"

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
        resized.save(path, 'PNG', optimize=True)
        with open(path, 'rb') as f:
            generated[filename] = f.read()
    return generated

VALUE_REPLACEMENTS = [
    ('RyukGram is an independent project inspired by SCInsta.', LUCID_FOOTER),
    ('O RyukGram é um projeto independente inspirado no SCInsta.', LUCID_FOOTER),
    ('Support RyukGram development', LUCID_FOOTER),
    ('Apoie o desenvolvimento do RyukGram', LUCID_FOOTER),
    ('Enjoying RyukGram?', 'Lucid Insta'),
    ('Gostando do RyukGram?', 'Lucid Insta'),
    ("It's free, and nothing leaves your device. If you enjoy using it, a coffee keeps it going.", LUCID_FOOTER),
    ('Donate to Ryuk', 'Lucid Insta'),
    ('Doe para Ryuk', 'Lucid Insta'),
    ('RyukGram developer', 'Lucid Edition'),
    ('Desenvolvedor RyukGram', 'Lucid Edition'),
    ('SCInsta developer', 'Lucid Suite'),
    ('Desenvolvedor do SCInsta', 'Lucid Suite'),
    ('BHInstagram developer', 'Lucid Suite'),
    ('Desenvolvedor do BHInstagram', 'Lucid Suite'),
    ('Version, credits, and links', 'Versão e detalhes'),
    ('Versão, créditos e links', 'Versão e detalhes'),
    ('Credits', 'Sobre o Lucid'),
    ('Créditos', 'Sobre o Lucid'),
    ('Developers', 'Edição'),
    ('Desenvolvedores', 'Edição'),
    ('Join Telegram channel', 'Lucid Insta'),
    ('Junte-se ao canal Telegram', 'Lucid Insta'),
    ('Get it on Telegram', 'Lucid Insta'),
    ('Telegram channel', 'Lucid Insta'),
    ('Canal de telegrama', 'Lucid Insta'),
    ('View on GitHub', 'Lucid Insta'),
    ('Ver no GitHub', 'Lucid Insta'),
    ('Open GitHub', 'Lucid Insta'),
    ('Abra o GitHub', 'Lucid Insta'),
    ('Appreciate the support', LUCID_FOOTER),
    ('Obrigado pelo apoio', LUCID_FOOTER),
    ('Donate', 'Lucid'),
    ('Doar', 'Lucid'),
    ('RyukGram', 'Lucid Insta'),
    ('ryukgram', 'lucid_insta'),
    ('SCInsta', 'Lucid Suite'),
    ('scinsta', 'lucid_suite'),
    ('BHInstagram', 'Lucid Suite'),
    ('bhinstagram', 'lucid_suite'),
    ('faroukbmiled', 'Lucid'),
    ('BandarHL', 'Lucid'),
    ('SoCuul', 'Lucid'),
    ('axryuk', 'lucid'),
]

# Matches `"key" = "value";` in Apple .strings files while respecting escaped quotes `\"` and multiline strings.
STRINGS_PAIR_RE = re.compile(
    r'("(?:\\.|[^"\\])*")(\s*=\s*)("(?:\\.|[^"\\])*")(\s*;)',
    re.DOTALL
)

def clean_value_text(val_inner):
    out = val_inner
    for old, new in VALUE_REPLACEMENTS:
        out = out.replace(old, new)
    return out

def clean_strings_preserving_keys(content):
    """Rewrites ONLY the right-hand side localized values so NSBundle lookup keys never break."""
    def _repl(match):
        key_lit, eq_sep, val_lit, semi = match.groups()
        inner = val_lit[1:-1]
        cleaned_inner = clean_value_text(inner)
        return f'{key_lit}{eq_sep}"{cleaned_inner}"{semi}'

    return STRINGS_PAIR_RE.sub(_repl, content)

def clean_and_slim_bundle(bundle_dir):
    if not os.path.exists(bundle_dir):
        return

    removed_bytes = 0
    for root, dirs, files in os.walk(bundle_dir, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            low = file.lower()

            # 1. Strip third-party banner art & C headers / license bloat inside frameworks
            if low == 'ryukgram.png' or low.startswith('license') or low.endswith('.h') or low.endswith('.modulemap'):
                try:
                    removed_bytes += os.path.getsize(file_path)
                    os.remove(file_path)
                except OSError:
                    pass
                continue

            # 2. Brand Localizable.strings without corrupting left-hand keys
            if file == 'Localizable.strings':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    cleaned = clean_strings_preserving_keys(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned)
                    print(f"Branded values (keys preserved): {file_path}")
                except Exception as e:
                    print(f"Error patching {file_path}: {e}")

        for d in dirs:
            if d in ('Headers', 'Modules', 'PrivateHeaders'):
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)

    print(f"Slimmed RyukGram.bundle: removed {removed_bytes / 1024:.1f} KB of headers/licenses/banners.")

def patch_base_ipa():
    input_ipa = 'packages/com.burbn.instagram.ipa'
    if not os.path.exists(input_ipa):
        input_ipa = 'com.burbn.instagram.ipa'
    if not os.path.exists(input_ipa):
        print("Base IPA not present locally; skipping IPA repack step.")
        return

    output_ipa = 'packages/BaseInstagram-branded.ipa'
    os.makedirs('packages', exist_ok=True)

    print("Preparing Liquid Glass icons...")
    icon_map = generate_app_icons('AppIcon1024.png', 'temp_icons')

    print(f"Branding and slimming {input_ipa} -> {output_ipa}...")
    stripped_count = 0
    with zipfile.ZipFile(input_ipa, 'r') as zin, zipfile.ZipFile(output_ipa, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            filename = item.filename

            # Strip dead FairPlay DRM metadata & PlugIns extensions upfront to save ~10+ MB and App IDs
            if '/SC_Info/' in filename or '/PlugIns/' in filename or '/Watch/' in filename:
                stripped_count += 1
                continue

            # 1. Update main app Info.plist
            if filename.endswith('.app/Info.plist') and 'Payload/' in filename and 'PlugIns/' not in filename:
                data = zin.read(filename)
                pl = plistlib.loads(data)
                pl['CFBundleDisplayName'] = 'Lucid Insta'
                pl['CFBundleName'] = 'Lucid Insta'
                pl.pop('UISupportedDevices', None)
                new_data = plistlib.dumps(pl, fmt=plistlib.FMT_BINARY)
                zout.writestr(item, new_data)
                print(f"Patched {filename} -> DisplayName: Lucid Insta")

            # 2. Replace App Icons
            elif any(filename.endswith('/' + k) for k in icon_map):
                base_k = os.path.basename(filename)
                zout.writestr(item, icon_map[base_k])
                print(f"Replaced {filename} with Liquid Glass icon")

            else:
                zout.writestr(item, zin.read(filename))

    shutil.rmtree('temp_icons', ignore_errors=True)
    print(f"Base IPA branded successfully! Stripped {stripped_count} dead DRM/extension entries.")

if __name__ == '__main__':
    clean_and_slim_bundle('packages/RyukGram.bundle')
    patch_base_ipa()
