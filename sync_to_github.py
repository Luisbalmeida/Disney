#!/usr/bin/env python3
"""
Script para sincronizar o histórico de atrações com GitHub automaticamente.
Uso: python sync_to_github.py
"""

import os
import subprocess
from datetime import datetime

def run_command(cmd):
    """Executa um comando shell"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def sync_visited_attractions():
    """Sincroniza o ficheiro de histórico com GitHub"""
    
    # Verificar se ficheiro existe
    if not os.path.exists("visited_attractions.json"):
        print("❌ Ficheiro visited_attractions.json não encontrado!")
        return False
    
    print("🔄 A sincronizar histórico com GitHub...")
    
    # 1. Add ficheiro
    print("1️⃣ Adicionando ficheiro...")
    code, out, err = run_command("git add visited_attractions.json")
    if code != 0:
        print(f"❌ Erro ao adicionar: {err}")
        return False
    print("✅ Ficheiro adicionado")
    
    # 2. Verificar se há mudanças
    code, out, err = run_command("git status --porcelain visited_attractions.json")
    if not out.strip():
        print("ℹ️ Sem mudanças para sincronizar")
        return True
    
    # 3. Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Atualizar histórico de atrações [auto-sync {timestamp}]"
    print(f"2️⃣ Fazendo commit: {commit_msg}")
    code, out, err = run_command(f'git commit -m "{commit_msg}"')
    if code != 0:
        print(f"❌ Erro ao fazer commit: {err}")
        return False
    print("✅ Commit realizado")
    
    # 4. Push
    print("3️⃣ Fazendo push para GitHub...")
    code, out, err = run_command("git push origin main")
    if code != 0:
        print(f"❌ Erro ao fazer push: {err}")
        return False
    print("✅ Push realizado com sucesso!")
    
    return True

def show_statistics():
    """Mostra estatísticas do ficheiro"""
    import json
    
    if not os.path.exists("visited_attractions.json"):
        print("Sem dados ainda")
        return
    
    with open("visited_attractions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    visitadas = data.get("visitadas", {})
    print("\n📊 Estatísticas Atuais:")
    print(f"   Total de atrações visitadas: {len(visitadas)}")
    
    if visitadas:
        tempos = [v.get("tempo_espera", 0) for v in visitadas.values()]
        print(f"   Tempo total economizado: {sum(tempos)} min")
        print(f"   Tempo médio de espera: {sum(tempos)/len(tempos):.1f} min")

if __name__ == "__main__":
    print("🏰 Disney AI - Sincronizador de Histórico")
    print("=" * 50)
    
    if sync_visited_attractions():
        print("\n✨ Sincronização completa!")
        show_statistics()
    else:
        print("\n❌ Erro na sincronização!")
        exit(1)
