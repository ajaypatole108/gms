import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today, now_datetime


class GymClassBooking(Document):
	def validate(self):
		self.validate_member_membership()
		self.validate_class_capacity()
		self.validate_booking_time()
		self.set_booking_date()

	def validate_member_membership(self):
		"""Validate member's membership status"""
		member = frappe.get_doc("Gym Member", self.member)
		if not member.is_membership_valid():
			frappe.throw(_("Member's membership is not valid. Please check membership status."))

	def validate_class_capacity(self):
		"""Validate class capacity"""
		class_doc = frappe.get_doc("Gym Class", self.gym_class)
		
		# Check if class is fully booked
		existing_bookings = frappe.get_all(
			"Gym Class Booking",
			filters={
				"gym_class": self.gym_class,
				"class_date": self.class_date,
				"class_time": self.class_time,
				"status": "Confirmed"
			}
		)
		
		if len(existing_bookings) >= class_doc.max_capacity:
			frappe.throw(_("Class is fully booked for this time slot"))

	def validate_booking_time(self):
		"""Validate booking time is not in the past"""
		booking_datetime = frappe.utils.get_datetime(f"{self.class_date} {self.class_time}")
		if booking_datetime < now_datetime():
			frappe.throw(_("Cannot book classes in the past"))

	def set_booking_date(self):
		"""Set booking date to current datetime"""
		if not self.booking_date:
			self.booking_date = now_datetime()

	def on_submit(self):
		"""Update class statistics when booking is confirmed"""
		self.update_class_statistics()

	def update_class_statistics(self):
		"""Update class booking statistics"""
		# This could trigger notifications or update analytics
		pass

	def cancel_booking(self, reason=None):
		"""Cancel the class booking"""
		if self.status == "Cancelled":
			frappe.throw(_("Booking is already cancelled"))
		
		if self.status == "Completed":
			frappe.throw(_("Cannot cancel completed booking"))
		
		self.status = "Cancelled"
		self.cancellation_reason = reason
		self.save()

	def mark_completed(self):
		"""Mark booking as completed"""
		if self.status != "Confirmed":
			frappe.throw(_("Only confirmed bookings can be marked as completed"))
		
		self.status = "Completed"
		self.save()

	def mark_no_show(self):
		"""Mark booking as no show"""
		if self.status != "Confirmed":
			frappe.throw(_("Only confirmed bookings can be marked as no show"))
		
		self.status = "No Show"
		self.save()

	def get_booking_summary(self):
		"""Get booking summary information"""
		class_doc = frappe.get_doc("Gym Class", self.gym_class)
		member_doc = frappe.get_doc("Gym Member", self.member)
		
		return {
			"booking_id": self.name,
			"member_name": f"{member_doc.first_name} {member_doc.last_name}",
			"class_name": class_doc.class_name,
			"class_type": class_doc.class_type,
			"trainer": class_doc.trainer,
			"class_date": self.class_date,
			"class_time": self.class_time,
			"status": self.status,
			"amount_paid": self.amount_paid,
			"currency": self.currency
		}


@frappe.whitelist()
def book_class(member_id, class_id, class_date, class_time):
	"""Book a class for a member"""
	# Validate member
	member = frappe.get_doc("Gym Member", member_id)
	if not member.is_membership_valid():
		return {"status": "error", "message": "Membership is not valid"}
	
	# Get class details
	class_doc = frappe.get_doc("Gym Class", class_id)
	
	# Check if class exists and is active
	if not class_doc.is_active:
		return {"status": "error", "message": "Class is not active"}
	
	# Check capacity
	if class_doc.is_fully_booked(class_date, class_time):
		return {"status": "error", "message": "Class is fully booked"}
	
	# Check if member already booked this class
	existing_booking = frappe.get_all(
		"Gym Class Booking",
		filters={
			"member": member_id,
			"gym_class": class_id,
			"class_date": class_date,
			"class_time": class_time
		}
	)
	
	if existing_booking:
		return {"status": "error", "message": "Already booked this class"}
	
	# Create booking
	booking = frappe.get_doc({
		"doctype": "Gym Class Booking",
		"member": member_id,
		"gym_class": class_id,
		"class_date": class_date,
		"class_time": class_time,
		"status": "Confirmed",
		"amount_paid": class_doc.price,
		"currency": class_doc.currency
	})
	booking.insert()
	
	return {
		"status": "success",
		"message": "Class booked successfully",
		"booking_id": booking.name
	}


@frappe.whitelist()
def cancel_booking(booking_id, reason=None):
	"""Cancel a class booking"""
	booking = frappe.get_doc("Gym Class Booking", booking_id)
	booking.cancel_booking(reason)
	
	return {"status": "success", "message": "Booking cancelled successfully"}


@frappe.whitelist()
def get_member_bookings(member_id, status=None):
	"""Get all bookings for a member"""
	filters = {"member": member_id}
	if status:
		filters["status"] = status
	
	return frappe.get_all(
		"Gym Class Booking",
		filters=filters,
		fields=["*"],
		order_by="class_date desc, class_time desc"
	)


@frappe.whitelist()
def get_class_bookings(class_id, class_date=None):
	"""Get all bookings for a class"""
	filters = {"gym_class": class_id}
	if class_date:
		filters["class_date"] = class_date
	
	return frappe.get_all(
		"Gym Class Booking",
		filters=filters,
		fields=["*"],
		order_by="class_date asc, class_time asc"
	)


@frappe.whitelist()
def get_booking_statistics(start_date=None, end_date=None):
	"""Get booking statistics for a date range"""
	if not start_date:
		start_date = today()
	if not end_date:
		end_date = today()
	
	bookings = frappe.get_all(
		"Gym Class Booking",
		filters={
			"class_date": ["between", [start_date, end_date]]
		},
		fields=["status"]
	)
	
	total_bookings = len(bookings)
	confirmed_bookings = len([b for b in bookings if b.status == "Confirmed"])
	cancelled_bookings = len([b for b in bookings if b.status == "Cancelled"])
	completed_bookings = len([b for b in bookings if b.status == "Completed"])
	no_show_bookings = len([b for b in bookings if b.status == "No Show"])
	
	return {
		"total_bookings": total_bookings,
		"confirmed_bookings": confirmed_bookings,
		"cancelled_bookings": cancelled_bookings,
		"completed_bookings": completed_bookings,
		"no_show_bookings": no_show_bookings,
		"attendance_rate": (completed_bookings / confirmed_bookings * 100) if confirmed_bookings > 0 else 0
	}
