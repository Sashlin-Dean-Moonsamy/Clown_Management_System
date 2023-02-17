# Clown_Management_System
A clown management system built with flask microservices


Microservices:

	1.Authentication Service: Handles authentication of clowns, troupe leaders and clients

	2.Client Service: Allows clients to view their appointments and rate past appointments

	3. Troupe Leader Service: Allows troupe leaders to create appointments for clowns

	4. Clown Service: Allows clowns to view and manage their appointments and report issues or request client contact details


APIs:

	5. Authentication API: Provides endpoints for authentication of clowns, troupe leaders and clients
	
	6. Client API: Provides endpoints for client to view their appointments and rate past appointments
	
	7. Troupe Leader API: Provides endpoints for troupe leaders to create appointments for clowns
	
	8. Clown API: Provides endpoints for clowns to view and manage their appointments and report issues or request client contact details


Tools:

	9. Docker: To containerize the microservices for deployment

	10. Troupe Leader Service communicates with Clown Service to create appointments for clowns.

	11. Clown Service communicates with Client Service to retrieve client information for appointment management.
