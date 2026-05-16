
CREATE TABLE user_ (
	id_user	 BIGSERIAL,
	username VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	password VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_user)
);

CREATE TABLE admin_ (
	user__id_user BIGINT,
	PRIMARY KEY(user__id_user)
);

CREATE TABLE airport_ (
	airport_code	 BIGSERIAL,
	city		 VARCHAR(512) NOT NULL,
	name		 VARCHAR(512) NOT NULL,
	country		 VARCHAR(512) NOT NULL,
	admin__user__id_user BIGINT NOT NULL,
	PRIMARY KEY(airport_code)
);

CREATE TABLE crew (
	crew_id			 BIGSERIAL,
	admin__user__id_user	 BIGINT NOT NULL,
	crew_members_user__id_user BIGINT NOT NULL,
	PRIMARY KEY(crew_id)
);

CREATE TABLE passanger (
	user__id_user BIGINT,
	PRIMARY KEY(user__id_user)
);

CREATE TABLE flight_ (
	flight_code		 BIGSERIAL,
	departure_time	 TIME NOT NULL,
	arrival_time		 TIME NOT NULL,
	existing_seats	 BIGINT NOT NULL,
	crew_crew_id		 BIGINT NOT NULL,
	admin__user__id_user	 BIGINT NOT NULL,
	airport__airport_code	 BIGINT NOT NULL,
	airport__airport_code1 BIGINT NOT NULL,
	PRIMARY KEY(flight_code)
);

CREATE TABLE schedule_ (
	flight_date		 DATE NOT NULL,
	admin__user__id_user BIGINT NOT NULL,
	crew_crew_id	 BIGINT NOT NULL,
	PRIMARY KEY(flight_date)
);

CREATE TABLE ticket_ (
	name			 VARCHAR(512) ,
	vat			 VARCHAR(512),
	booking_booking_id	 BIGINT,
	seat_schedule__flight_date DATE NOT NULL,
	seat_flight__flight_code	 BIGINT NOT NULL,
    seat_number VARCHAR(512) NOT NULL;
	PRIMARY KEY(booking_booking_id,seat_schedule__flight_date,seat_flight__flight_code,seat_number)
);

CREATE TABLE booking (
	booking_id		 BIGSERIAL,
	ticket_quantity	 INTEGER NOT NULL,
	ticket_amout_to_pay	 FLOAT(8) NOT NULL,
	ticket_amout_payed	 FLOAT(8) NOT NULL DEFAULT 0,
	flight__flight_code	 BIGINT NOT NULL,
	schedule__flight_date	 DATE NOT NULL,
	passanger_user__id_user BIGINT NOT NULL,
	PRIMARY KEY(booking_id)
);

CREATE TABLE payment (
	payment_id	 BIGSERIAL,
	amount_payed	 FLOAT(8) NOT NULL,
	payment_date	 TIMESTAMP NOT NULL,
	booking_booking_id BIGINT NOT NULL,
	PRIMARY KEY(payment_id)
);

CREATE TABLE payment_method (
	method		 VARCHAR(512) NOT NULL,
	payment_payment_id BIGINT,
	PRIMARY KEY(payment_payment_id)
);

CREATE TABLE seat (
	available		 BOOL NOT NULL,
	seat_number		 BIGINT NOT NULL,
	schedule__flight_date DATE,
	flight__flight_code	 BIGINT,
	PRIMARY KEY(schedule__flight_date,flight__flight_code)
);

CREATE TABLE crew_members (
	admin__user__id_user BIGINT NOT NULL,
	user__id_user	 BIGINT,
	PRIMARY KEY(user__id_user)
);

CREATE TABLE flight_attendant (
	crew_crew_id		 BIGINT NOT NULL,
	crew_members_user__id_user BIGINT,
	PRIMARY KEY(crew_members_user__id_user)
);

CREATE TABLE pilot (
	crew_crew_id		 BIGINT NOT NULL,
	crew_members_user__id_user BIGINT,
	PRIMARY KEY(crew_members_user__id_user)
);

CREATE TABLE flight__schedule_ (
	flight__flight_code	 BIGINT,
	schedule__flight_date DATE,
	PRIMARY KEY(flight__flight_code,schedule__flight_date)
);


CREATE TABLE credit_card (
	payment_payment_id BIGINT,
	PRIMARY KEY(payment_payment_id)
);

CREATE TABLE debt_card (
	payment_payment_id BIGINT,
	PRIMARY KEY(payment_payment_id)
);

CREATE TABLE mbway (
	payment_payment_id BIGINT,
	PRIMARY KEY(payment_payment_id)
);


ALTER TABLE user_ ADD UNIQUE (username, email);
ALTER TABLE admin_ ADD CONSTRAINT admin__fk1 FOREIGN KEY (user__id_user) REFERENCES user_(id_user);
ALTER TABLE airport_ ADD CONSTRAINT airport__fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE crew ADD CONSTRAINT crew_fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE crew ADD CONSTRAINT crew_fk2 FOREIGN KEY (crew_members_user__id_user) REFERENCES crew_members(user__id_user);
ALTER TABLE passanger ADD CONSTRAINT passanger_fk1 FOREIGN KEY (user__id_user) REFERENCES user_(id_user);
ALTER TABLE flight_ ADD CONSTRAINT flight__fk1 FOREIGN KEY (crew_crew_id) REFERENCES crew(crew_id);
ALTER TABLE flight_ ADD CONSTRAINT flight__fk2 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE flight_ ADD CONSTRAINT flight__fk3 FOREIGN KEY (airport__airport_code) REFERENCES airport_(airport_code);
ALTER TABLE flight_ ADD CONSTRAINT flight__fk4 FOREIGN KEY (airport__airport_code1) REFERENCES airport_(airport_code);
ALTER TABLE schedule_ ADD CONSTRAINT schedule__fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE schedule_ ADD CONSTRAINT schedule__fk2 FOREIGN KEY (crew_crew_id) REFERENCES crew(crew_id);
ALTER TABLE ticket_ ADD UNIQUE (seat_schedule__flight_date, seat_flight__flight_code,seat_number);
ALTER TABLE ticket_ ADD CONSTRAINT ticket__fk1 FOREIGN KEY (booking_booking_id) REFERENCES booking(booking_id);
ALTER TABLE ticket_ ADD CONSTRAINT ticket__fk2 FOREIGN KEY (seat_schedule__flight_date, seat_flight__flight_code,seat_number) REFERENCES seat(schedule__flight_date, flight__flight_code,seat_number);
ALTER TABLE ticket_ ADD CONSTRAINT constraint_0 CHECK (CHECK (LENGT(vat) = 9));
ALTER TABLE booking ADD CONSTRAINT booking_fk1 FOREIGN KEY (flight__flight_code) REFERENCES flight_(flight_code);
ALTER TABLE booking ADD CONSTRAINT booking_fk2 FOREIGN KEY (schedule__flight_date) REFERENCES schedule_(flight_date);
ALTER TABLE booking ADD CONSTRAINT booking_fk3 FOREIGN KEY (passanger_user__id_user) REFERENCES passanger(user__id_user);
ALTER TABLE payment ADD CONSTRAINT payment_fk1 FOREIGN KEY (booking_booking_id) REFERENCES booking(booking_id);
ALTER TABLE seat ADD CONSTRAINT seat_fk1 FOREIGN KEY (schedule__flight_date) REFERENCES schedule_(flight_date);
ALTER TABLE seat ADD CONSTRAINT seat_fk2 FOREIGN KEY (flight__flight_code) REFERENCES flight_(flight_code);
ALTER TABLE crew_members ADD CONSTRAINT crew_members_fk1 FOREIGN KEY (admin__user__id_user) REFERENCES admin_(user__id_user);
ALTER TABLE crew_members ADD CONSTRAINT crew_members_fk2 FOREIGN KEY (user__id_user) REFERENCES user_(id_user);
ALTER TABLE flight_attendante ADD CONSTRAINT flight_attendante_fk1 FOREIGN KEY (crew_crew_id) REFERENCES crew(crew_id);
ALTER TABLE flight_attendante ADD CONSTRAINT flight_attendante_fk2 FOREIGN KEY (crew_members_user__id_user) REFERENCES crew_members(user__id_user);
ALTER TABLE pilot ADD CONSTRAINT pilot_fk1 FOREIGN KEY (crew_crew_id) REFERENCES crew(crew_id);
ALTER TABLE pilot ADD CONSTRAINT pilot_fk2 FOREIGN KEY (crew_members_user__id_user) REFERENCES crew_members(user__id_user);
ALTER TABLE flight__schedule_ ADD CONSTRAINT flight__schedule__fk1 FOREIGN KEY (flight__flight_code) REFERENCES flight_(flight_code);
ALTER TABLE flight__schedule_ ADD CONSTRAINT flight__schedule__fk2 FOREIGN KEY (schedule__flight_date) REFERENCES schedule_(flight_date);
ALTER TABLE credit_card ADD CONSTRAINT credit_card_fk1 FOREIGN KEY (payment_payment_id) REFERENCES payment(payment_id);
ALTER TABLE debt_card ADD CONSTRAINT debt_card_fk1 FOREIGN KEY (payment_payment_id) REFERENCES payment(payment_id);
ALTER TABLE mbway ADD CONSTRAINT mbway_fk1 FOREIGN KEY (payment_payment_id) REFERENCES payment(payment_id);