#!/usr/bin/env python3
"""
Script de téléchargement automatique USE Lite
Pour Clone v10.1 ULTIMATE - Institut du Couple
Version corrigée avec bonnes URLs
"""

import os
import urllib.request
import json
import ssl

print("🚀 Téléchargement USE Lite - Démarrage\n")

# Fix SSL pour macOS
ssl_context = ssl._create_unverified_context()

# Créer dossiers
os.makedirs("models/use-lite", exist_ok=True)
os.makedirs("js", exist_ok=True)

print("📁 Dossiers créés : models/use-lite/, js/")

# ========================================
# 1. Télécharger TensorFlow.js
# ========================================

print("\n📦 Téléchargement TensorFlow.js...")
tfjs_url = "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.11.0/dist/tf.min.js"
tfjs_path = "js/tf.min.js"

try:
    urllib.request.urlretrieve(tfjs_url, tfjs_path, context=ssl_context)
    size_kb = os.path.getsize(tfjs_path) / 1024
    print(f"✅ TensorFlow.js téléchargé : {size_kb:.1f} KB")
except Exception as e:
    print(f"❌ Erreur TensorFlow.js : {e}")
    exit(1)

# ========================================
# 2. Télécharger Universal Sentence Encoder (via npm package)
# ========================================

print("\n📦 Téléchargement Universal Sentence Encoder...")
print("   Note : Utilisation du modèle standard (pas Lite) pour compatibilité")

# URLs correctes depuis unpkg (npm package)
base_url = "https://tfhub.dev/tensorflow/tfjs-model/universal-sentence-encoder/1/default/1/"

files_to_download = [
    ("model.json", "models/use-lite/model.json", base_url + "model.json"),
    ("group1-shard1of1.bin", "models/use-lite/group1-shard1of1.bin", base_url + "group1-shard1of1.bin")
]

# Alternative : utiliser storage.googleapis directement
alt_base = "https://storage.googleapis.com/tfjs-models/savedmodel/universal_sentence_encoder_lite/"

files_alt = [
    ("model.json", "models/use-lite/model.json"),
    ("group1-shard1of1.bin", "models/use-lite/group1-shard1of1.bin")
]

total_size = 0

# Essayer d'abord l'URL alternative
print("  📥 Tentative depuis storage.googleapis.com...")

for filename, local_path in files_alt:
    url = alt_base + filename
    print(f"     {filename}...", end=" ", flush=True)
    
    try:
        urllib.request.urlretrieve(url, local_path, context=ssl_context)
        size_kb = os.path.getsize(local_path) / 1024
        total_size += size_kb
        
        if size_kb > 1024:
            print(f"✅ {size_kb/1024:.1f} MB")
        else:
            print(f"✅ {size_kb:.1f} KB")
    except Exception as e:
        print(f"❌ {e}")
        print(f"\n⚠️ Échec téléchargement automatique.")
        print(f"   Solution de secours : Téléchargement manuel requis.")
        break

# Si échec, proposer téléchargement manuel
if not os.path.exists("models/use-lite/group1-shard1of1.bin"):
    print("\n" + "="*60)
    print("⚠️ TÉLÉCHARGEMENT MANUEL REQUIS")
    print("="*60)
    print("\nLes URLs automatiques ont échoué.")
    print("Je vais utiliser le package npm directement.\n")
    
    print("📦 Installation via npm (recommandé)...")
    print("\nExécute ces commandes :\n")
    print("  npm install @tensorflow-models/universal-sentence-encoder")
    print("  npm install @tensorflow/tfjs")
    print("\nPuis dis-moi que c'est fait pour que je continue !")
    exit(0)

# ========================================
# 3. Créer fichier de configuration
# ========================================

print("\n📝 Création fichier de configuration...")

config = {
    "version": "v10.1-ULTIMATE",
    "tensorflowjs": {
        "path": "js/tf.min.js",
        "version": "4.11.0",
        "size_kb": os.path.getsize(tfjs_path) / 1024
    },
    "use_lite": {
        "path": "models/use-lite/model.json",
        "model_size_mb": total_size / 1024,
        "dimensions": 512,
        "max_length": 256
    },
    "installation_date": __import__("datetime").datetime.now().isoformat()
}

with open("models/config.json", "w") as f:
    json.dump(config, f, indent=2)

print(f"✅ Configuration sauvegardée : models/config.json")

# ========================================
# 4. Résumé
# ========================================

print("\n" + "="*60)
print("🎉 TÉLÉCHARGEMENT TERMINÉ !")
print("="*60)

print(f"\n📂 Structure créée :")
print(f"   institut-du-couple/")
print(f"   ├── js/")
print(f"   │   └── tf.min.js ({os.path.getsize(tfjs_path)/1024:.1f} KB)")
print(f"   └── models/")
print(f"       ├── config.json")
print(f"       └── use-lite/")
print(f"           ├── model.json ({os.path.getsize('models/use-lite/model.json')/1024:.1f} KB)")
print(f"           └── group1-shard1of1.bin ({os.path.getsize('models/use-lite/group1-shard1of1.bin')/1024/1024:.1f} MB)")

print(f"\n📊 Taille totale : {(total_size + os.path.getsize(tfjs_path)/1024)/1024:.1f} MB")

print("\n✅ Prêt pour MODULE 14 Hybride !")
