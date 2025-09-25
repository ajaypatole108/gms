import frappe
from frappe.model.document import Document
from frappe import _


class GymMembershipPlan(Document):
	def validate(self):
		self.validate_visit_limits()
		self.validate_pricing()

	def validate_visit_limits(self):
		"""Validate visit limits configuration"""
		if not self.unlimited_visits and (not self.max_visits_per_month or self.max_visits_per_month <= 0):
			frappe.throw(_("Please specify maximum visits per month or enable unlimited visits"))

	def validate_pricing(self):
		"""Validate pricing information"""
		if self.price <= 0:
			frappe.throw(_("Price must be greater than 0"))
		
		if self.duration_months <= 0:
			frappe.throw(_("Duration must be greater than 0 months"))

	def get_monthly_price(self):
		"""Calculate monthly price"""
		if self.duration_months > 0:
			return self.price / self.duration_months
		return self.price

	def get_daily_price(self):
		"""Calculate daily price"""
		monthly_price = self.get_monthly_price()
		return monthly_price / 30  # Approximate daily price

	def is_visit_allowed(self, member_visits_this_month):
		"""Check if member can make another visit this month"""
		if self.unlimited_visits:
			return True
		
		return member_visits_this_month < self.max_visits_per_month

	def get_plan_summary(self):
		"""Get a summary of the plan"""
		summary = {
			"name": self.plan_name,
			"type": self.plan_type,
			"duration": f"{self.duration_months} month(s)",
			"price": f"{self.currency} {self.price}",
			"monthly_price": f"{self.currency} {self.get_monthly_price():.2f}",
			"visits": "Unlimited" if self.unlimited_visits else f"{self.max_visits_per_month} per month"
		}
		return summary


@frappe.whitelist()
def get_active_plans():
	"""Get all active membership plans"""
	return frappe.get_all(
		"Gym Membership Plan",
		filters={"is_active": 1},
		fields=["*"],
		order_by="price asc"
	)


@frappe.whitelist()
def get_plan_comparison():
	"""Get plan comparison data"""
	plans = frappe.get_all(
		"Gym Membership Plan",
		filters={"is_active": 1},
		fields=["*"],
		order_by="price asc"
	)
	
	comparison_data = []
	for plan in plans:
		plan_doc = frappe.get_doc("Gym Membership Plan", plan.name)
		comparison_data.append(plan_doc.get_plan_summary())
	
	return comparison_data