**Prompt 1** RF1 
Eres un estudiante de ingenieria informatica y necesito que dentro del entorno que ya cree hagas esto:
Modelo de datos y administración 
• Los modelos respetan los tipos, las relaciones y las restricciones únicas del diagrama. 
• No se puede eliminar una categoría que tenga productos ni un producto que figure en algún 
pedido. 
• Todos los modelos se administran desde Django Admin, con una representación legible, 
búsqueda y filtros. El detalle de un pedido se ve dentro del propio pedido. 
• El proyecto incluye datos de prueba que se pueden cargar: al menos 4 categorías y 20 productos 
(alguno sin stock y alguno no disponible), un encargado y dos clientes.



Que se corrigio?
No mucho, solo algunas cosas que no habia hecho bien como que hizo 10 productos en vez de 20.

**Prompt 2** RF 2

Ahora necesito que me crees autenticacion y roles que cumplan estas condiciones:
 Solo los usuarios autenticados pueden usar la aplicación, que permite iniciar y cerrar sesión. 
• Hay dos roles: cliente y encargado (is_staff). Cada rol accede solo a sus funciones: si un 
cliente entra a una dirección del encargado, se le niega el acceso. 
• La sesión expira a los 30 minutos. 
• El menú muestra el usuario conectado y su rol.

Que se corrigio?
Como que el prompt me registro la mitad, no se porque asi que tuve que reingresar lo de que la sesion expiraba a los 30 mintos y el menu muestra el usuario, pero lo hizo bien

**Prompt 3:** RF3

Necesito ahora un catalogo para clientes el cual cumpla con :
El cliente ve los productos disponibles de categorías activas, con buscador por nombre y filtro 
por categoría. 
• Los precios se muestran en pesos chilenos, con separador de miles (por ejemplo, $1.500). 
• Un producto sin stock se muestra como agotado y no se puede agregar al carrito. 

Que corrigio?
Nada, hizo todo bien.