import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime, get_datetime
from frappe import _


class GymVisit(Document):
	def validate(self):
		self.validate_member_membership()
		self.validate_visit_times()
		self.calculate_duration()

	def validate_member_membership(self):
		"""Validate member's membership status"""
		member = frappe.get_doc("Gym Member", self.member)
		if not member.is_membership_valid():
			frappe.throw(_("Member's membership is not valid. Please check membership status."))

	def validate_visit_times(self):
		"""Validate check-in and check-out times"""
		if self.check_out_time and self.check_in_time:
			if self.check_out_time <= self.check_in_time:
				frappe.throw(_("Check-out time must be after check-in time"))

	def calculate_duration(self):
		"""Calculate visit duration in minutes"""
		if self.check_in_time and self.check_out_time:
			check_in_datetime = get_datetime(f"{self.visit_date} {self.check_in_time}")
			check_out_datetime = get_datetime(f"{self.visit_date} {self.check_out_time}")
			duration = check_out_datetime - check_in_datetime
			self.duration_minutes = int(duration.total_seconds() / 60)

	def on_submit(self):
		"""Update member's visit statistics"""
		self.update_member_visit_stats()

	def update_member_visit_stats(self):
		"""Update member's visit statistics"""
		member = frappe.get_doc("Gym Member", self.member)
		member.record_visit()
		
		# Update monthly visit count for membership plan validation
		self.update_monthly_visit_count()

	def update_monthly_visit_count(self):
		"""Update monthly visit count for membership plan validation"""
		# This would be used to check against membership plan limits
		# Implementation depends on how you want to track monthly visits
		pass

	def check_out(self, check_out_time=None):
		"""Check out the member"""
		if not check_out_time:
			check_out_time = now_datetime().time()
		
		self.check_out_time = check_out_time
		self.calculate_duration()
		self.save()

	@frappe.whitelist()
	def get_visit_summary(self):
		"""Get visit summary for the member"""
		return {
			"visit_date": self.visit_date,
			"duration": self.duration_minutes,
			"visit_type": self.visit_type,
			"trainer": self.trainer,
			"equipment_count": len(self.equipment_used) if self.equipment_used else 0
		}


@frappe.whitelist()
def check_in_member(member_id, visit_type="Regular Workout", trainer=None):
	"""Check in a member"""
	# Validate member
	member = frappe.get_doc("Gym Member", member_id)
	if not member.is_membership_valid():
		frappe.throw(_("Member's membership is not valid"))
	
	# Check if member is already checked in today
	existing_visit = frappe.get_all(
		"Gym Visit",
		filters={
			"member": member_id,
			"visit_date": today(),
			"check_out_time": ["is", "not set"]
		}
	)
	
	if existing_visit:
		frappe.throw(_("Member is already checked in today"))
	
	# Create new visit
	visit = frappe.get_doc({
		"doctype": "Gym Visit",
		"member": member_id,
		"visit_date": today(),
		"check_in_time": now_datetime().time(),
		"visit_type": visit_type,
		"trainer": trainer
	})
	visit.insert()
	return visit


@frappe.whitelist()
def check_out_member(member_id):
	"""Check out a member"""
	# Find active visit
	visit = frappe.get_all(
		"Gym Visit",
		filters={
			"member": member_id,
			"visit_date": today(),
			"check_out_time": ["is", "not set"]
		},
		limit=1
	)
	
	if not visit:
		frappe.throw(_("No active visit found for this member"))
	
	visit_doc = frappe.get_doc("Gym Visit", visit[0].name)
	visit_doc.check_out()
	return visit_doc


@frappe.whitelist()
def get_member_visit_history(member_id, limit=10):
	"""Get member's visit history"""
	return frappe.get_all(
		"Gym Visit",
		filters={"member": member_id},
		fields=["*"],
		order_by="visit_date desc, check_in_time desc",
		limit=limit
	)


@frappe.whitelist()
def get_daily_visits(date=None):
	"""Get all visits for a specific date"""
	if not date:
		date = today()
	
	return frappe.get_all(
		"Gym Visit",
		filters={"visit_date": date},
		fields=["*"],
		order_by="check_in_time asc"
	)


@frappe.whitelist()
def get_visit_statistics(start_date=None, end_date=None):
	"""Get visit statistics for a date range"""
	if not start_date:
		start_date = today()
	if not end_date:
		end_date = today()
	
	visits = frappe.get_all(
		"Gym Visit",
		filters={
			"visit_date": ["between", [start_date, end_date]]
		},
		fields=["*"]
	)
	
	total_visits = len(visits)
	total_duration = sum(visit.duration_minutes or 0 for visit in visits)
	unique_members = len(set(visit.member for visit in visits))
	
	return {
		"total_visits": total_visits,
		"total_duration_minutes": total_duration,
		"total_duration_hours": total_duration / 60,
		"unique_members": unique_members,
		"average_duration": total_duration / total_visits if total_visits > 0 else 0
	}
