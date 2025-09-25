import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime, add_days, get_datetime
from frappe import _


class GymMember(Document):
	def validate(self):
		self.validate_membership_dates()
		self.validate_contact_info()
		self.set_member_id()

	def set_member_id(self):
		"""Auto-generate member ID if not set"""
		if not self.member_id:
			self.member_id = self.name

	def validate_membership_dates(self):
		"""Validate membership start and end dates"""
		if self.membership_start_date and self.membership_end_date:
			if self.membership_start_date > self.membership_end_date:
				frappe.throw(_("Membership start date cannot be after end date"))

	def validate_contact_info(self):
		"""Validate email and mobile number format"""
		if self.email and not frappe.utils.validate_email_address(self.email):
			frappe.throw(_("Please enter a valid email address"))
		
		if self.mobile_no and not frappe.utils.validate_phone_number(self.mobile_no):
			frappe.throw(_("Please enter a valid mobile number"))

	def on_update(self):
		"""Update membership status based on dates"""
		self.update_membership_status()

	def update_membership_status(self):
		"""Update membership status based on current date and membership dates"""
		if not self.membership_end_date:
			return
		
		today_date = today()
		
		if self.membership_end_date < today_date:
			if self.membership_status != "Expired":
				self.membership_status = "Expired"
				self.is_active = 0
		elif self.membership_start_date and self.membership_start_date > today_date:
			if self.membership_status != "Inactive":
				self.membership_status = "Inactive"
				self.is_active = 0
		else:
			if self.membership_status in ["Expired", "Inactive"]:
				self.membership_status = "Active"
				self.is_active = 1

	def record_visit(self):
		"""Record a gym visit for this member"""
		self.last_visit = now_datetime()
		self.total_visits = (self.total_visits or 0) + 1
		self.save()

	def get_membership_days_remaining(self):
		"""Get number of days remaining in membership"""
		if not self.membership_end_date:
			return None
		
		remaining_days = (get_datetime(self.membership_end_date) - get_datetime(today())).days
		return max(0, remaining_days)

	def is_membership_valid(self):
		"""Check if membership is currently valid"""
		if not self.membership_end_date:
			return False
		
		return self.membership_end_date >= today() and self.is_active

	def extend_membership(self, days):
		"""Extend membership by specified number of days"""
		if not self.membership_end_date:
			frappe.throw(_("No membership end date found"))
		
		self.membership_end_date = add_days(self.membership_end_date, days)
		self.update_membership_status()
		self.save()

	def suspend_membership(self, reason=None):
		"""Suspend the membership"""
		self.membership_status = "Suspended"
		self.is_active = 0
		if reason:
			self.notes = (self.notes or "") + f"\nSuspended: {reason}"
		self.save()

	def reactivate_membership(self):
		"""Reactivate the membership"""
		if self.membership_end_date and self.membership_end_date >= today():
			self.membership_status = "Active"
			self.is_active = 1
			self.save()
		else:
			frappe.throw(_("Cannot reactivate expired membership"))


@frappe.whitelist()
def get_member_dashboard_data(member_id):
	"""Get dashboard data for a specific member"""
	member = frappe.get_doc("Gym Member", member_id)
	
	return {
		"member": member,
		"membership_days_remaining": member.get_membership_days_remaining(),
		"is_membership_valid": member.is_membership_valid(),
		"recent_visits": get_recent_visits(member_id),
		"upcoming_classes": get_upcoming_classes(member_id)
	}


def get_recent_visits(member_id, limit=5):
	"""Get recent visits for a member"""
	return frappe.get_all(
		"Gym Visit",
		filters={"member": member_id},
		fields=["*"],
		order_by="visit_time desc",
		limit=limit
	)


def get_upcoming_classes(member_id, limit=5):
	"""Get upcoming classes for a member"""
	return frappe.get_all(
		"Gym Class Booking",
		filters={
			"member": member_id,
			"status": "Confirmed",
			"class_date": [">=", today()]
		},
		fields=["*"],
		order_by="class_date asc",
		limit=limit
	)
