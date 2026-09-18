## Description

¡Hola! Te paso esto. Los restaurantes con mucho walk-in tienen los viernes colas de 30 a 40 personas en la puerta, anotadas en un cuaderno. Se pierden nombres, la gente se va sin avisar y el anfitrión no da abasto. Queremos una lista de espera digital:

El comensal escanea un QR en la puerta, pone su nombre, su teléfono y cuántos son, y entra a la cola.
En su celular ve su posición en vivo —que baja con una animación cuando avanza la cola— y un tiempo estimado de espera.
Cuando su mesa está lista le llega un WhatsApp con dos botones: «Voy en camino» y «Ya no voy».
El anfitrión ve la cola en su tablet, puede arrastrar para reordenar (a veces priorizan a un cliente frecuente) y toca «Llamar».
Al cierre del día, un reporte: cuánta gente se fue sin sentarse.
Te adjunto el prototipo, son cinco pantallas. Es para un piloto con tres locales —La Terraza Azul y Cuatro Vientos en Lima, y Casa Mediterránea en Santiago— en tres semanas. ¿Qué necesitas?


### Stack
Python y FastAPI en el backend, React con TypeScript en el frontend, MySQL. Todo corre en Google Cloud, sobre Cloud Run.


### Países
Perú, Chile, Ecuador y Colombia. Este piloto: dos locales en Lima y uno en Santiago.

### El Libro
El sistema que ya usan los restaurantes.
Más antiguo, escrito en PHP. Tiene los locales, sus mesas y sus reservas. También tiene una lista de espera que casi nadie usa: exige iniciar sesión y pasar por cuatro pantallas.


### Anfitriones
Usan tablets compartidas en la entrada. Los viernes hay dos atendiendo a la vez.
La puerta
El wifi es malo. El comensal usa sus datos móviles.

### WhatsApp
Hay una cuenta de WhatsApp Business. Los mensajes que inicia el negocio necesitan plantillas aprobadas por Meta —que a veces las rechaza— y se cobran por mensaje, con una tarifa distinta por país. También hay un proveedor de SMS contratado.
Escala
Tres locales en el piloto, con hasta 40 personas en cola por local un viernes. Si funciona, la idea es llevarlo a 150 locales en tres meses.


## Notes

* This is a demo for production if anything is vague let's confirm with questions.
* The objective is not to implement everything but to prioritize what's important for a demo.
* If something is not in the UI do not add it yet. this is tbc with design


### Out of Scope

1. QR code generation is out of scope. For now use a single restaurant. Since there is no QR code the "join" screen is associated to that single restaurant.
2. In the waiting screen, elapsed time is out of scope, given that we don't have enough data yet. Animation of the current position is out of scope.
3. Given that whatsapp templates require approval and that can block, whatsapp is out of scope. Instead the confirmation UI can be triggered when the host clicks on "llamar", and be a Web UI instead. 
4. There is a sms provider but given that this is a demo. There is not much sense in including it. 
5. Final Report is out of scope too
6. In the host view, reordering and dragging is out of scope 
7. Cloud implementation


### Observations

El libro will be used as seeder
Use polling for updating data in the UI
Tests cover the state transition and concurrency-sensitive behavior. 
The API stores one waitlist entry and returns a private status token.
The DB choice is SQLite, and operations are done in a separate layer. In services and repositories style. 
No show is automatic for now, we don't have 
The host screen is an operational tool, so stale state and conflicting actions matter more than animation.
“Position” becomes ambiguous if hosts can reorder the queue or choose a party based on table size.
“Call” is a state change; “notification delivered” is a separate outcome.
The report requires more terminal states than the prototype shows.
Rejoining must create a new visit, or historical metrics will become incorrect.
The system must work with multiple tablets and later multiple Cloud Run instances.
A public guest flow requires an access mechanism that does not expose sequential IDs or other guests' details.

### Missing decisions

Exact queue ordering rules.
What happens after the ten-minute call window.
Whether no-show is automatic or confirmed by a host.
Whether guests may move backward in the displayed queue.
How a guest recovers their status page on another device.
What happens when the notification provider accepts, rejects, times out, or delivers late.
Which system owns the waitlist during the pilot.
Definition of a restaurant “day” after midnight.



