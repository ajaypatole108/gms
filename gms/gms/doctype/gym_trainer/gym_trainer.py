import frappe
from frappe.model.document import Document
from frappe import _


class GymTrainer(Document):
	def validate(self):
		self.validate_contact_info()
		self.validate_working_hours()

	def validate_contact_info(self):
		"""Validate email and mobile number format"""
		if self.email and not frappe.utils.validate_email_address(self.email):
			frappe.throw(_("Please enter a valid email address"))
		
		if self.mobile_no and not frappe.utils.validate_phone_number(self.mobile_no):
			frappe.throw(_("Please enter a valid mobile number"))

	def validate_working_hours(self):
		"""Validate working hours configuration"""
		if self.working_hours:
			for hour in self.working_hours:
				if hour.start_time and hour.end_time:
					if hour.start_time >= hour.end_time:
						frappe.throw(_("Start time must be before end time for {0}").format(hour.day_of_week))

	def get_available_classes(self):
		"""Get classes assigned to this trainer"""
		return frappe.get_all(
			"Gym Class",
			filters={"trainer": self.name, "is_active": 1},
			fields=["*"]
		)

	def get_trainer_schedule(self, date=None):
		"""Get trainer's schedule for a specific date"""
		if not date:
			date = frappe.utils.today()
		
		day_of_week = frappe.utils.get_datetime(date).strftime("%A")
		
		# Get working hours for the day
		working_hours = []
		if self.working_hours:
			for hour in self.working_hours:
				if hour.day_of_week == day_of_week and hour.is_active:
					working_hours.append({
						"start_time": hour.start_time,
						"end_time": hour.end_time
					})
		
		# Get classes for the day
		classes = frappe.get_all(
			"Gym Class",
			filters={"trainer": self.name, "is_active": 1},
			fields=["*"]
		)
		
		scheduled_classes = []
		for class_doc in classes:
			class_info = frappe.get_doc("Gym Class", class_doc.name)
			for schedule in class_info.schedule:
				if schedule.day_of_week == day_of_week and schedule.is_active:
					scheduled_classes.append({
						"class_name": class_doc.class_name,
						"start_time": schedule.start_time,
						"end_time": schedule.end_time,
						"class_type": class_doc.class_type
					})
		
		return {
			"working_hours": working_hours,
			"scheduled_classes": scheduled_classes
		}

	def is_available(self, date, start_time, end_time):
		"""Check if trainer is available at specific time"""
		schedule = self.get_trainer_schedule(date)
		
		# Check if within working hours
		within_working_hours = False
		for hour in schedule["working_hours"]:
			if start_time >= hour["start_time"] and end_time <= hour["end_time"]:
				within_working_hours = True
				break
		
		if not within_working_hours:
			return False
		
		# Check for class conflicts
		for class_info in schedule["scheduled_classes"]:
			if (start_time < class_info["end_time"] and end_time > class_info["start_time"]):
				return False
		
		return True

	def get_trainer_statistics(self):
		"""Get trainer performance statistics"""
		# Get total classes conducted
		total_classes = frappe.get_all(
			"Gym Class Booking",
			filters={
				"gym_class": ["in", [c.name for c in self.get_available_classes()]],
				"status": "Completed"
			}
		)
		
		# Get current month classes
		current_month = frappe.utils.today()[:7] + "-01"
		current_month_classes = frappe.get_all(
			"Gym Class Booking",
			filters={
				"gym_class": ["in", [c.name for c in self.get_available_classes()]],
				"status": "Completed",
				"class_date": [">=", current_month]
			}
		)
		
		return {
			"total_classes": len(total_classes),
			"current_month_classes": len(current_month_classes),
			"assigned_classes": len(self.get_available_classes())
		}


@frappe.whitelist()
def get_available_trainers(date=None, start_time=None, end_time=None):
	"""Get trainers available at specific time"""
	if not date:
		date = frappe.utils.today()
	
	trainers = frappe.get_all(
		"Gym Trainer",
		filters={"is_active": 1},
		fields=["*"]
	)
	
	available_trainers = []
	for trainer in trainers:
		trainer_doc = frappe.get_doc("Gym Trainer", trainer.name)
		if start_time and end_time:
			if trainer_doc.is_available(date, start_time, end_time):
				available_trainers.append(trainer)
		else:
			available_trainers.append(trainer)
	
	return available_trainers


@frappe.whitelist()
def get_trainer_dashboard_data(trainer_id):
	"""Get dashboard data for a specific trainer"""
	trainer = frappe.get_doc("Gym Trainer", trainer_id)
	
	return {
		"trainer": trainer,
		"statistics": trainer.get_trainer_statistics(),
		"assigned_classes": trainer.get_available_classes(),
		"schedule": trainer.get_trainer_schedule()
	}
