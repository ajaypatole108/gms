import frappe
from frappe import _
from frappe.utils import today, now_datetime, add_days
from frappe.model.document import Document


@frappe.whitelist()
def get_member_profile(member_id):
	"""Get complete member profile information"""
	member = frappe.get_doc("Gym Member", member_id)
	
	return {
		"member_id": member.member_id,
		"name": f"{member.first_name} {member.last_name}",
		"email": member.email,
		"mobile_no": member.mobile_no,
		"membership_status": member.membership_status,
		"membership_type": member.membership_type,
		"membership_start_date": member.membership_start_date,
		"membership_end_date": member.membership_end_date,
		"is_active": member.is_active,
		"last_visit": member.last_visit,
		"total_visits": member.total_visits,
		"membership_days_remaining": member.get_membership_days_remaining(),
		"is_membership_valid": member.is_membership_valid(),
		"photo": member.photo,
		"fitness_goals": member.fitness_goals,
		"preferred_trainer": member.preferred_trainer
	}


@frappe.whitelist()
def update_member_profile(member_id, data):
	"""Update member profile information"""
	member = frappe.get_doc("Gym Member", member_id)
	
	# Update allowed fields
	allowed_fields = [
		"first_name", "last_name", "mobile_no", "address", 
		"emergency_contact", "fitness_goals", "health_conditions", 
		"allergies", "preferred_trainer"
	]
	
	for field in allowed_fields:
		if field in data:
			member.set(field, data[field])
	
	member.save()
	return {"status": "success", "message": "Profile updated successfully"}


@frappe.whitelist()
def get_member_visit_history(member_id, limit=10):
	"""Get member's visit history"""
	visits = frappe.get_all(
		"Gym Visit",
		filters={"member": member_id},
		fields=["*"],
		order_by="visit_date desc, check_in_time desc",
		limit=limit
	)
	
	return visits


@frappe.whitelist()
def get_member_upcoming_classes(member_id, limit=5):
	"""Get member's upcoming class bookings"""
	bookings = frappe.get_all(
		"Gym Class Booking",
		filters={
			"member": member_id,
			"status": "Confirmed",
			"class_date": [">=", today()]
		},
		fields=["*"],
		order_by="class_date asc, class_time asc",
		limit=limit
	)
	
	return bookings


@frappe.whitelist()
def get_member_statistics(member_id):
	"""Get member's fitness statistics"""
	member = frappe.get_doc("Gym Member", member_id)
	
	# Get visit statistics for current month
	current_month_visits = frappe.get_all(
		"Gym Visit",
		filters={
			"member": member_id,
			"visit_date": [">=", today()[:7] + "-01"],  # First day of current month
			"visit_date": ["<=", today()]
		},
		fields=["duration_minutes"]
	)
	
	total_duration = sum(visit.duration_minutes or 0 for visit in current_month_visits)
	
	# Get class bookings for current month
	current_month_classes = frappe.get_all(
		"Gym Class Booking",
		filters={
			"member": member_id,
			"class_date": [">=", today()[:7] + "-01"],
			"class_date": ["<=", today()],
			"status": "Confirmed"
		}
	)
	
	return {
		"total_visits": member.total_visits,
		"current_month_visits": len(current_month_visits),
		"current_month_duration": total_duration,
		"current_month_classes": len(current_month_classes),
		"membership_days_remaining": member.get_membership_days_remaining(),
		"last_visit": member.last_visit
	}


@frappe.whitelist()
def check_in_member(member_id, visit_type="Regular Workout"):
	"""Check in a member to the gym"""
	# Validate member
	member = frappe.get_doc("Gym Member", member_id)
	if not member.is_membership_valid():
		return {"status": "error", "message": "Membership is not valid"}
	
	# Check if already checked in today
	existing_visit = frappe.get_all(
		"Gym Visit",
		filters={
			"member": member_id,
			"visit_date": today(),
			"check_out_time": ["is", "not set"]
		}
	)
	
	if existing_visit:
		return {"status": "error", "message": "Already checked in today"}
	
	# Create visit record
	visit = frappe.get_doc({
		"doctype": "Gym Visit",
		"member": member_id,
		"visit_date": today(),
		"check_in_time": now_datetime().time(),
		"visit_type": visit_type
	})
	visit.insert()
	
	return {
		"status": "success", 
		"message": "Checked in successfully",
		"visit_id": visit.name,
		"check_in_time": visit.check_in_time
	}


@frappe.whitelist()
def check_out_member(member_id):
	"""Check out a member from the gym"""
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
		return {"status": "error", "message": "No active visit found"}
	
	visit_doc = frappe.get_doc("Gym Visit", visit[0].name)
	visit_doc.check_out()
	
	return {
		"status": "success",
		"message": "Checked out successfully",
		"visit_duration": visit_doc.duration_minutes,
		"check_out_time": visit_doc.check_out_time
	}


@frappe.whitelist()
def book_class(member_id, class_name, class_date, class_time):
	"""Book a class for a member"""
	# Validate member
	member = frappe.get_doc("Gym Member", member_id)
	if not member.is_membership_valid():
		return {"status": "error", "message": "Membership is not valid"}
	
	# Get class details
	class_doc = frappe.get_doc("Gym Class", class_name)
	
	# Check if class exists and is active
	if not class_doc.is_active:
		return {"status": "error", "message": "Class is not active"}
	
	# Check capacity
	existing_bookings = frappe.get_all(
		"Gym Class Booking",
		filters={
			"gym_class": class_name,
			"class_date": class_date,
			"class_time": class_time,
			"status": "Confirmed"
		}
	)
	
	if len(existing_bookings) >= class_doc.max_capacity:
		return {"status": "error", "message": "Class is fully booked"}
	
	# Check if member already booked this class
	existing_booking = frappe.get_all(
		"Gym Class Booking",
		filters={
			"member": member_id,
			"gym_class": class_name,
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
		"gym_class": class_name,
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
def cancel_class_booking(booking_id, reason=None):
	"""Cancel a class booking"""
	booking = frappe.get_doc("Gym Class Booking", booking_id)
	
	if booking.status == "Cancelled":
		return {"status": "error", "message": "Booking already cancelled"}
	
	booking.status = "Cancelled"
	booking.cancellation_reason = reason
	booking.save()
	
	return {"status": "success", "message": "Booking cancelled successfully"}


@frappe.whitelist()
def get_available_classes(date=None):
	"""Get available classes for a specific date"""
	if not date:
		date = today()
	
	# Get all active classes
	classes = frappe.get_all(
		"Gym Class",
		filters={"is_active": 1},
		fields=["*"]
	)
	
	available_classes = []
	
	for class_doc in classes:
		class_info = frappe.get_doc("Gym Class", class_doc.name)
		
		# Get class schedule for the date
		day_of_week = frappe.utils.get_datetime(date).strftime("%A")
		
		for schedule in class_info.schedule:
			if schedule.day_of_week == day_of_week and schedule.is_active:
				# Check capacity
				bookings = frappe.get_all(
					"Gym Class Booking",
					filters={
						"gym_class": class_doc.name,
						"class_date": date,
						"class_time": schedule.start_time,
						"status": "Confirmed"
					}
				)
				
				available_spots = class_doc.max_capacity - len(bookings)
				
				available_classes.append({
					"class_name": class_doc.class_name,
					"class_type": class_doc.class_type,
					"trainer": class_doc.trainer,
					"start_time": schedule.start_time,
					"end_time": schedule.end_time,
					"duration": class_doc.duration_minutes,
					"price": class_doc.price,
					"currency": class_doc.currency,
					"available_spots": available_spots,
					"max_capacity": class_doc.max_capacity,
					"class_level": class_doc.class_level
				})
	
	return available_classes


@frappe.whitelist()
def get_member_dashboard(member_id):
	"""Get complete dashboard data for a member"""
	member = frappe.get_doc("Gym Member", member_id)
	
	return {
		"profile": get_member_profile(member_id),
		"statistics": get_member_statistics(member_id),
		"recent_visits": get_member_visit_history(member_id, 5),
		"upcoming_classes": get_member_upcoming_classes(member_id, 5),
		"available_classes": get_available_classes()
	}
