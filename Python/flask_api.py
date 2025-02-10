from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route('/calculo', methods=['POST'])
def calcular():
    try:
        data = request.get_json()
        valor = data['valor']
        data_inicio = data['data_inicio']
        data_fim = data['data_fim']
        indice = data['indice']

        print(f"Recebendo dados: valor={valor}, data_inicio={data_inicio}, data_fim={data_fim}, indice={indice}")

        dia_inicio, mes_inicio, ano_inicio = data_inicio.split("/")
        dia_fim, mes_fim, ano_fim = data_fim.split("/")
        
        # Configuração do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executar sem abrir janela
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-webgl")
        chrome_options.add_argument("--disable-accelerated-2d-canvas")
        chrome_options.add_argument("--disable-accelerated-graphics")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--enable-unsafe-swiftshader")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)


        try:
            driver.get("https://calculoexato.com.br/parprima.aspx?codMenu=FinanAtualizaIndice")
            wait = WebDriverWait(driver, 10)

            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

            print("Página carregada, iniciando preenchimento dos campos...")

            campo_valor = wait.until(EC.presence_of_element_located((By.ID, "txt1")))
            campo_valor.clear()  # Limpa o campo antes de inserir o valor
            campo_valor.send_keys(f"{valor:.2f}")  # Insere o novo valor
            
            # Selecionando o dia
            select_dia = Select(driver.find_element(By.ID, "comboDataDia2"))
            select_dia.select_by_value(dia_inicio)

            select_dia_fim = Select(driver.find_element(By.ID, "comboDataDia3"))
            select_dia_fim.select_by_value(dia_fim)

            # Selecionando o mês
            select_mes = Select(driver.find_element(By.ID, "comboDataMes2"))
            select_mes.select_by_value(mes_inicio)

            select_mes_fim = Select(driver.find_element(By.ID, "comboDataMes3"))
            select_mes_fim.select_by_value(mes_fim)

            # Selecionando o ano
            select_ano = Select(driver.find_element(By.ID, "comboDataAno2"))
            select_ano.select_by_value(ano_inicio)

            select_ano_fim = Select(driver.find_element(By.ID, "comboDataAno3"))
            select_ano_fim.select_by_value(ano_fim)
            
            driver.find_element(By.ID, "comboIndice4").send_keys(indice)

            print("achou elementos")
            
            botao_continuar = wait.until(EC.visibility_of_element_located((By.ID, "btnContinuar")))
            ActionChains(driver).move_to_element(botao_continuar).click().perform()
            print("Botão clicado, aguardando resultado...")

            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

            # Pegando a primeira ocorrência com XPath e :nth-of-type()
            valor_atualizado_elemento = driver.find_element(By.XPATH, "(//p[b[contains(text(),'Valor atualizado')]])[1]")
            # Extraindo o valor
            valor_atualizado = valor_atualizado_elemento.text.split("R$")[1].strip()

            # Procurando a primeira ocorrência do texto "Em percentual"
            percentual_elemento = driver.find_element(By.XPATH, "(//p[contains(text(),'Em percentual')])[1]")
            # Extraindo o valor percentual
            percentual_final = percentual_elemento.text.split("Em percentual:")[1].split("%")[0].strip()

            # Procurando a primeira ocorrência do texto "Em fator de multiplicação"
            multiplicacao_elemento = driver.find_element(By.XPATH, "//p[contains(., 'Em fator de multiplicação:')]")
            # Extraindo o valor do fator de multiplicação
            fator_multiplicacao = multiplicacao_elemento.text.split("Em fator de multiplicação:")[1].splitlines()[0].strip()

            print("Recebeu valores")

            # Extraindo o texto correto da página
            lista_texto = driver.find_element(By.XPATH, "//p[contains(., 'Os valores do índice utilizados neste cálculo foram:')]")
            texto_meses = lista_texto.text.split("Os valores do índice utilizados neste cálculo foram:")[1].strip()

            # Dividindo os valores corretamente
            valores_lista = texto_meses.split("; ")

            # Criando um dicionário {mês: valor_float}
            valores_dict = {}
            for item in valores_lista:
                mes, valor_lista = item.split(" = ")
                
                # Removendo espaços e caracteres indesejados
                valor_lista = valor_lista.replace(",", ".").replace("%", "").strip()
                
                # Removendo ponto final, caso haja
                if valor_lista.endswith("."):
                    valor_lista = valor_lista[:-1]
                
                # Convertendo para float
                valor_lista = float(valor_lista)
                
                # Adicionando ao dicionário
                valores_dict[mes] = valor_lista

            # Encontrando os meses com menor e maior porcentagem
            menor_mes = min(valores_dict, key=valores_dict.get)  
            maior_mes = max(valores_dict, key=valores_dict.get)  

            menor_valor = valores_dict[menor_mes]  
            maior_valor = valores_dict[maior_mes]  

            # Criando as strings formatadas
            menor_percentual = f"{menor_mes} ({menor_valor:.2f}%)"
            maior_percentual = f"{maior_mes} ({maior_valor:.2f}%)"

            # Formatando a lista de meses
            lista_formatada = "\n".join([f"o {item.strip()}" for item in valores_lista if item.strip()])

            # Convertendo para float
            valor_atualizado = float(valor_atualizado.replace(".", "").replace(",", ".").strip())
            fator_multiplicacao = float(fator_multiplicacao.replace(",", ".").strip())
            percentual_final = float(percentual_final.replace(",", ".").strip())

            # Formatando os valores com as casas decimais corretas
            valor_atualizado = f"{valor_atualizado:.2f}"
            fator_multiplicacao = f"{fator_multiplicacao:.6f}"
            percentual_final = f"{percentual_final:.4f}"


            sucesso_return = "Consulta realizada com sucesso!"

            return jsonify({
                'BOLEANO': True,
                'Valor a ser atualizado': valor,
                'Data inicio': data_inicio,
                'Data fim': data_fim,
                'Indice de atualizacao': indice,
                'Valor atualizado': valor_atualizado,
                'Percentual final': percentual_final,
                'Fator multiplicacao': fator_multiplicacao,
                'Lista de meses': lista_formatada,
                'Maior percentual': maior_percentual,
                'Menor percentual': menor_percentual,
                'Texto de retorno': sucesso_return   
            })

        finally:
            driver.quit()

    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
