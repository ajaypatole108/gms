import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, add_months
from frappe import _


class GymEquipment(Document):
	def validate(self):
		self.validate_dates()
		self.validate_serial_number()
		self.set_next_maintenance_date()

	def validate_dates(self):
		"""Validate date fields"""
		if self.purchase_date and self.warranty_expiry_date:
			if self.purchase_date > self.warranty_expiry_date:
				frappe.throw(_("Purchase date cannot be after warranty expiry date"))
		
		if self.last_maintenance_date and self.next_maintenance_date:
			if self.last_maintenance_date > self.next_maintenance_date:
				frappe.throw(_("Last maintenance date cannot be after next maintenance date"))

	def validate_serial_number(self):
		"""Validate unique serial number"""
		if self.serial_number:
			existing = frappe.get_all(
				"Gym Equipment",
				filters={
					"serial_number": self.serial_number,
					"name": ["!=", self.name]
				}
			)
			if existing:
				frappe.throw(_("Serial number already exists"))

	def set_next_maintenance_date(self):
		"""Set next maintenance date based on maintenance schedule"""
		if self.maintenance_schedule and not self.next_maintenance_date:
			# Get the most frequent maintenance interval
			intervals = [row.maintenance_interval_days for row in self.maintenance_schedule if row.maintenance_interval_days]
			if intervals:
				min_interval = min(intervals)
				self.next_maintenance_date = add_days(today(), min_interval)

	def on_update(self):
		"""Update equipment status based on maintenance dates"""
		self.update_equipment_status()

	def update_equipment_status(self):
		"""Update equipment status based on maintenance and warranty dates"""
		today_date = today()
		
		# Check warranty expiry
		if self.warranty_expiry_date and self.warranty_expiry_date < today_date:
			if self.status != "Out of Order":
				self.status = "Out of Order"
				self.notes = (self.notes or "") + f"\nWarranty expired on {self.warranty_expiry_date}"
		
		# Check maintenance due
		elif self.next_maintenance_date and self.next_maintenance_date <= today_date:
			if self.status == "Operational":
				self.status = "Under Maintenance"
				self.notes = (self.notes or "") + f"\nMaintenance due on {self.next_maintenance_date}"

	def schedule_maintenance(self, maintenance_type, scheduled_date, notes=None):
		"""Schedule maintenance for the equipment"""
		maintenance = frappe.get_doc({
			"doctype": "Gym Equipment Maintenance",
			"equipment": self.name,
			"maintenance_type": maintenance_type,
			"scheduled_date": scheduled_date,
			"status": "Scheduled",
			"notes": notes
		})
		maintenance.insert()
		return maintenance

	def complete_maintenance(self, maintenance_id, actual_date=None, notes=None):
		"""Complete a maintenance task"""
		maintenance = frappe.get_doc("Gym Equipment Maintenance", maintenance_id)
		maintenance.status = "Completed"
		maintenance.actual_date = actual_date or today()
		maintenance.completion_notes = notes
		maintenance.save()
		
		# Update equipment maintenance dates
		self.last_maintenance_date = maintenance.actual_date
		self.set_next_maintenance_date()
		self.status = "Operational"
		self.save()

	def get_maintenance_history(self):
		"""Get maintenance history for this equipment"""
		return frappe.get_all(
			"Gym Equipment Maintenance",
			filters={"equipment": self.name},
			fields=["*"],
			order_by="scheduled_date desc"
		)

	def get_usage_statistics(self):
		"""Get usage statistics for this equipment"""
		# This would integrate with gym visit tracking
		# For now, return basic info
		return {
			"total_usage_hours": 0,  # Would be calculated from visit logs
			"average_daily_usage": 0,
			"last_used": None
		}

	def is_available(self):
		"""Check if equipment is available for use"""
		return self.status == "Operational" and self.is_active

	def get_equipment_age(self):
		"""Get equipment age in days"""
		if not self.purchase_date:
			return None
		
		return (today() - self.purchase_date).days


@frappe.whitelist()
def get_equipment_by_location(location):
	"""Get all equipment in a specific location"""
	return frappe.get_all(
		"Gym Equipment",
		filters={
			"location": location,
			"is_active": 1
		},
		fields=["*"],
		order_by="equipment_name"
	)


@frappe.whitelist()
def get_equipment_by_type(equipment_type):
	"""Get all equipment of a specific type"""
	return frappe.get_all(
		"Gym Equipment",
		filters={
			"equipment_type": equipment_type,
			"is_active": 1
		},
		fields=["*"],
		order_by="equipment_name"
	)


@frappe.whitelist()
def get_maintenance_due_equipment():
	"""Get equipment that needs maintenance"""
	return frappe.get_all(
		"Gym Equipment",
		filters={
			"next_maintenance_date": ["<=", today()],
			"status": ["!=", "Under Maintenance"],
			"is_active": 1
		},
		fields=["*"],
		order_by="next_maintenance_date asc"
	)


@frappe.whitelist()
def get_equipment_dashboard_data():
	"""Get equipment dashboard data"""
	total_equipment = frappe.count("Gym Equipment", filters={"is_active": 1})
	operational = frappe.count("Gym Equipment", filters={"status": "Operational", "is_active": 1})
	under_maintenance = frappe.count("Gym Equipment", filters={"status": "Under Maintenance", "is_active": 1})
	out_of_order = frappe.count("Gym Equipment", filters={"status": "Out of Order", "is_active": 1})
	
	return {
		"total_equipment": total_equipment,
		"operational": operational,
		"under_maintenance": under_maintenance,
		"out_of_order": out_of_order,
		"operational_percentage": (operational / total_equipment * 100) if total_equipment > 0 else 0
	}
