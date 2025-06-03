✈️ UML Class Diagram — DjangoAir ERP System
📘 Description
This is a UML class diagram describing the architecture of the airline ERP system DjangoAir.
It covers all key entities of the project and shows their relationships: from users and tickets to flights, airplanes, and staff roles.

📐 Main Classes and Descriptions
👤 User
Base entity extended by all roles.

Fields:

id: int

email: str

password: str

role: str <<enum>> — supervisor / checkin / gate / passenger

🧍 Passenger
One-to-one relation with User

Fields:

first_name, last_name

balance: float

check_in_status: str

🛫 Flight
Fields:

flight_number, origin, destination

departure, arrival, status

Relations:

One-to-one with Airplane

One-to-one with SeatType

One-to-many with Ticket

🛩️ Airplane
Aircraft model

Fields: model: str, seats_total: int

💺 SeatType
Seat class: economy, business, etc.

Fields: name: str, class_type: str

🎫 Ticket
Central entity linking:

Passenger, Flight

Payment, Discount, Option

Fields:

price: float, seat_number: str

booking_date, create_dt

🎁 Option
Additional services

Fields: name: str, price: float

Relation: many-to-many with Ticket

🎟️ Discount
Promotions and coupons

Fields: code: str, percentage: float

💳 Payment
Payment details

Fields:

amount: float, status: str

payment_date, created_dt

👨‍✈️ Staff Roles
Supervisor
Inherits from User, can manage other staff members.

CheckinManager
Handles check-ins and luggage services.

GateManager
Responsible for boarding control.

