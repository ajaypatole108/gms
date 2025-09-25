import frappe
from frappe.model.document import Document
from frappe import _


class GymClass(Document):
	def validate(self):
		self.validate_capacity()
		self.validate_schedule()
		self.validate_trainer_availability()

	def validate_capacity(self):
		"""Validate class capacity"""
		if self.max_capacity <= 0:
			frappe.throw(_("Maximum capacity must be greater than 0"))

	def validate_schedule(self):
		"""Validate class schedule"""
		if not self.schedule:
			frappe.throw(_("Please add at least one schedule entry"))
		
		for schedule in self.schedule:
			if schedule.start_time and schedule.end_time:
				if schedule.start_time >= schedule.end_time:
					frappe.throw(_("Start time must be before end time for {0}").format(schedule.day_of_week))

	def validate_trainer_availability(self):
		"""Validate trainer availability for scheduled times"""
		if not self.trainer:
			return
		
		trainer = frappe.get_doc("Gym Trainer", self.trainer)
		
		for schedule in self.schedule:
			if schedule.is_active:
				if not trainer.is_available(None, schedule.start_time, schedule.end_time):
					frappe.throw(_("Trainer {0} is not available at {1} on {2}").format(
						self.trainer, schedule.start_time, schedule.day_of_week
					))

	def get_available_slots(self, date):
		"""Get available booking slots for a specific date"""
		day_of_week = frappe.utils.get_datetime(date).strftime("%A")
		
		available_slots = []
		for schedule in self.schedule:
			if schedule.day_of_week == day_of_week and schedule.is_active:
				# Check current bookings
				bookings = frappe.get_all(
					"Gym Class Booking",
					filters={
						"gym_class": self.name,
						"class_date": date,
						"class_time": schedule.start_time,
						"status": "Confirmed"
					}
				)
				
				available_spots = self.max_capacity - len(bookings)
				
				available_slots.append({
					"start_time": schedule.start_time,
					"end_time": schedule.end_time,
					"available_spots": available_spots,
					"max_capacity": self.max_capacity,
					"is_fully_booked": available_spots <= 0
				})
		
		return available_slots

	def get_class_statistics(self):
		"""Get class performance statistics"""
		# Get total bookings
		total_bookings = frappe.get_all(
			"Gym Class Booking",
			filters={"gym_class": self.name},
			fields=["status"]
		)
		
		# Get current month bookings
		current_month = frappe.utils.today()[:7] + "-01"
		current_month_bookings = frappe.get_all(
			"Gym Class Booking",
			filters={
				"gym_class": self.name,
				"class_date": [">=", current_month]
			},
			fields=["status"]
		)
		
		# Calculate statistics
		confirmed_bookings = len([b for b in total_bookings if b.status == "Confirmed"])
		cancelled_bookings = len([b for b in total_bookings if b.status == "Cancelled"])
		completed_bookings = len([b for b in total_bookings if b.status == "Completed"])
		
		return {
			"total_bookings": len(total_bookings),
			"confirmed_bookings": confirmed_bookings,
			"cancelled_bookings": cancelled_bookings,
			"completed_bookings": completed_bookings,
			"current_month_bookings": len(current_month_bookings),
			"attendance_rate": (completed_bookings / confirmed_bookings * 100) if confirmed_bookings > 0 else 0
		}

	def is_fully_booked(self, date, start_time):
		"""Check if class is fully booked for specific date and time"""
		bookings = frappe.get_all(
			"Gym Class Booking",
			filters={
				"gym_class": self.name,
				"class_date": date,
				"class_time": start_time,
				"status": "Confirmed"
			}
		)
		
		return len(bookings) >= self.max_capacity

	def get_class_revenue(self, start_date=None, end_date=None):
		"""Get class revenue for a date range"""
		if not start_date:
			start_date = frappe.utils.today()
		if not end_date:
			end_date = frappe.utils.today()
		
		bookings = frappe.get_all(
			"Gym Class Booking",
			filters={
				"gym_class": self.name,
				"class_date": ["between", [start_date, end_date]],
				"status": "Confirmed"
			},
			fields=["amount_paid"]
		)
		
		total_revenue = sum(booking.amount_paid or 0 for booking in bookings)
		return total_revenue


@frappe.whitelist()
def get_classes_by_trainer(trainer_id):
	"""Get all classes assigned to a specific trainer"""
	return frappe.get_all(
		"Gym Class",
		filters={"trainer": trainer_id, "is_active": 1},
		fields=["*"],
		order_by="class_name"
	)


@frappe.whitelist()
def get_classes_by_type(class_type):
	"""Get all classes of a specific type"""
	return frappe.get_all(
		"Gym Class",
		filters={"class_type": class_type, "is_active": 1},
		fields=["*"],
		order_by="class_name"
	)


@frappe.whitelist()
def get_class_schedule(class_id, date):
	"""Get class schedule for a specific date"""
	class_doc = frappe.get_doc("Gym Class", class_id)
	return class_doc.get_available_slots(date)


@frappe.whitelist()
def get_class_dashboard_data(class_id):
	"""Get dashboard data for a specific class"""
	class_doc = frappe.get_doc("Gym Class", class_id)
	
	return {
		"class": class_doc,
		"statistics": class_doc.get_class_statistics(),
		"revenue": class_doc.get_class_revenue(),
		"schedule": class_doc.schedule
	}
