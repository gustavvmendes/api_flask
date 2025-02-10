import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URI;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.net.SocketTimeoutException;

public class FinancialUpdateService {
    public static void main(String[] args) {
        // Parâmetros de entrada
        double valor = 50000.00;
        String dataInicio = "02/04/2021";
        String dataFim = "15/10/2024";
        String indice = "IGP-M";

        // Construindo o JSON com os parâmetros
        String jsonInputString = "{"
            + "\"valor\": " + valor + ","
            + "\"data_inicio\": \"" + dataInicio + "\","
            + "\"data_fim\": \"" + dataFim + "\","
            + "\"indice\": \"" + indice + "\""
            + "}";

        try {
            // URL da API Python
            URI uri = URI.create("http://127.0.0.1:5000/calculo");
            URL url = uri.toURL();
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            // Configurando os timeouts (em milissegundos)
            connection.setConnectTimeout(120000); // Tempo máximo para estabelecer a conexão: 120 segundos
            connection.setReadTimeout(120000);    // Tempo máximo para aguardar a resposta: 120 segundos

            // Envia a requisição JSON para a API Python
            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = jsonInputString.getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            // Recebe a resposta da API Python
            try (BufferedReader br = new BufferedReader(new InputStreamReader(connection.getInputStream(), "utf-8"))) {
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = br.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                System.out.println("Resposta da API: " + response.toString());
            }
        } catch (SocketTimeoutException e) {
            // Caso o tempo limite seja excedido
            System.out.println("Tempo limite de 120 segundos expirado.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
