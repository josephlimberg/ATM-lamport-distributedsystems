Implementación de sincronización de procesos y exclusión mutua usando Relojes de Lamport
Implementation of process synchronization and mutual exclusion using Lamport Clocks
## Descripción del Proyecto
Este proyecto implementa un sistema distribuido que simula retiros bancarios concurrentes hacia una base de datos MySQL compartida. Su objetivo principal es aplicar modelos de sincronización para coordinar procesos y asegurar el acceso seguro a recursos mediante **Relojes Lógicos de Lamport** y un algoritmo de **exclusión mutua** centralizado.

El sistema consta de:
1. **Un Servidor Central (Python):** Actúa como coordinador de la exclusión mutua y gestor del recurso (Base de Datos). Maneja una cola de prioridad para las peticiones.
2. **Proceso Distribuido 1 (Cliente Python):** Un cajero simulado desarrollado en Python.
3. **Proceso Distribuido 2 (Cliente Java):** Un cajero simulado desarrollado en Java.

### 1. Sincronización de Eventos y Orden Lógico
El sistema implementa estrictamente los **Relojes Lógicos de Lamport**. La regla de sincronización aplicada es:
* Antes de enviar un mensaje, el proceso incrementa su reloj local en 1.
* Al recibir un mensaje, el proceso actualiza su reloj a `max(Reloj_Local, Reloj_Mensaje) + 1`.


### 2. Exclusión Mutua y Eficiencia de Red
El servidor central gestiona el acceso al recurso compartido (la base de datos) insertando las peticiones en una cola de prioridad. El servidor otorga el permiso de acceso (`GRANT`) estrictamente al proceso con la marca de tiempo lógica más antigua en la cola.

El flujo completo de una transacción es altamente eficiente en tráfico de red, requiriendo **5 mensajes** en total:
1. `REQUEST` (Cliente -> Servidor): Petición para entrar a la sección crítica.
2. `GRANT` (Servidor -> Cliente): Otorgamiento del acceso.
3. `WITHDRAW` (Cliente -> Servidor): Ejecución del retiro bancario.
4. `APROBADO/RECHAZADO` (Servidor -> Cliente): Respuesta de la base de datos con el nuevo saldo.
5. `RELEASE` (Cliente -> Servidor): Liberación del recurso para el siguiente en la cola.

### 3. Control de Concurrencia y Condiciones de Carrera
Para evitar conflictos de concurrencia cuando los procesos de Python y Java envían peticiones en el mismo milisegundo, el servidor multihilo utiliza un sistema de cerrojos (`threading.Lock()`). Esto garantiza que la lectura y escritura del reloj global del servidor, la gestión de la cola y las transacciones SQL se ejecuten de manera atómica, previniendo cualquier estado inconsistente.
