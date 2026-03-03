import java.io.*;
import java.net.*;
import java.util.Scanner;

public class ClienteBanco {
    private static Socket socket;
    private static PrintWriter out;
    private static BufferedReader in;
    private static String id = "cajero_java";
    private static int relojLogico = 0;

    public static void main(String[] args) {
        // Variable para la IP del servidor
        String ipServidor = "IP_DEL_SERVIDOR"; 
        
        try {
            // Conexión al servidor (Reemplazar variable con la IP pública de tu VM)
            socket = new Socket(ipServidor, 7000); 
            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            out.println(id);

            Scanner sc = new Scanner(System.in);
            while (true) {
                System.out.print("\nPresiona ENTER para intentar retirar desde cajero Java...");
                sc.nextLine();

                relojLogico++;
                out.println("REQUEST," + relojLogico);
                System.out.println("[" + id + "] solicitando acceso (Reloj=" + relojLogico + ")...");

                String response = in.readLine();
                String[] partesResponse = response.split(",");
                String cmd = partesResponse[0];
                int tsServer = Integer.parseInt(partesResponse[1]);

                relojLogico = Math.max(relojLogico, tsServer) + 1;
                System.out.println("[" + id + "] Servidor dice: " + cmd + " | Reloj actualizado a: " + relojLogico);

                if (cmd.equals("GRANT")) {
                    System.out.println("[" + id + "] accede al banco, retirando $50...");
                    
                    relojLogico++;
                    out.println("WITHDRAW," + relojLogico);
                    
                    String resultadoRaw = in.readLine();
                    String[] partesResultado = resultadoRaw.split(",");
                    String resCmd = partesResultado[0];
                    int resTs = Integer.parseInt(partesResultado[1]);
                    String resSaldo = partesResultado[2];

                    relojLogico = Math.max(relojLogico, resTs) + 1;
                    System.out.println("[" + id + "] Resultado: " + resCmd + " (Saldo: " + resSaldo + ") | Reloj: " + relojLogico);
                    
                    Thread.sleep(2000);
                    
                    relojLogico++;
                    out.println("RELEASE," + relojLogico);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}