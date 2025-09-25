import frappe
from frappe import _


def after_install():
	"""Setup initial data after GMS installation"""
	setup_initial_data()


def setup_initial_data():
	"""Create initial data for the gym management system"""
	
	# Create sample membership plans
	create_sample_membership_plans()
	
	# Create sample equipment
	create_sample_equipment()
	
	# Create sample trainers
	create_sample_trainers()
	
	# Create sample classes
	create_sample_classes()
	
	# Create sample members
	create_sample_members()
	
	frappe.db.commit()
	frappe.msgprint(_("Sample data created successfully!"))


def create_sample_membership_plans():
	"""Create sample membership plans"""
	
	plans = [
		{
			"plan_name": "Basic Monthly",
			"plan_type": "Basic",
			"duration_months": 1,
			"price": 29.99,
			"currency": "USD",
			"unlimited_visits": 1,
			"description": "Basic monthly membership with unlimited gym access",
			"features": [
				{"feature_name": "Gym Access", "description": "Unlimited gym access", "is_included": 1},
				{"feature_name": "Locker Room", "description": "Access to locker room", "is_included": 1},
				{"feature_name": "Basic Equipment", "description": "Access to basic equipment", "is_included": 1}
			]
		},
		{
			"plan_name": "Premium Monthly",
			"plan_type": "Premium",
			"duration_months": 1,
			"price": 49.99,
			"currency": "USD",
			"unlimited_visits": 1,
			"description": "Premium monthly membership with additional benefits",
			"features": [
				{"feature_name": "Gym Access", "description": "Unlimited gym access", "is_included": 1},
				{"feature_name": "Locker Room", "description": "Access to locker room", "is_included": 1},
				{"feature_name": "All Equipment", "description": "Access to all equipment", "is_included": 1},
				{"feature_name": "Group Classes", "description": "Access to group classes", "is_included": 1},
				{"feature_name": "Sauna", "description": "Access to sauna", "is_included": 1}
			]
		},
		{
			"plan_name": "VIP Monthly",
			"plan_type": "VIP",
			"duration_months": 1,
			"price": 79.99,
			"currency": "USD",
			"unlimited_visits": 1,
			"description": "VIP monthly membership with premium benefits",
			"features": [
				{"feature_name": "Gym Access", "description": "Unlimited gym access", "is_included": 1},
				{"feature_name": "Locker Room", "description": "Access to locker room", "is_included": 1},
				{"feature_name": "All Equipment", "description": "Access to all equipment", "is_included": 1},
				{"feature_name": "Group Classes", "description": "Access to group classes", "is_included": 1},
				{"feature_name": "Sauna", "description": "Access to sauna", "is_included": 1},
				{"feature_name": "Personal Training", "description": "2 personal training sessions", "is_included": 1},
				{"feature_name": "Nutrition Consultation", "description": "Monthly nutrition consultation", "is_included": 1}
			]
		}
	]
	
	for plan_data in plans:
		if not frappe.db.exists("Gym Membership Plan", plan_data["plan_name"]):
			plan = frappe.get_doc({
				"doctype": "Gym Membership Plan",
				**plan_data
			})
			plan.insert()


def create_sample_equipment():
	"""Create sample gym equipment"""
	
	equipment_list = [
		{
			"equipment_name": "Treadmill 001",
			"equipment_type": "Cardio",
			"brand": "Life Fitness",
			"model": "Platinum Club Series",
			"location": "Cardio Zone",
			"status": "Operational",
			"purchase_date": "2023-01-15",
			"purchase_price": 3500.00,
			"currency": "USD",
			"description": "High-end treadmill with advanced features"
		},
		{
			"equipment_name": "Elliptical 001",
			"equipment_type": "Cardio",
			"brand": "Precor",
			"model": "EFX 835",
			"location": "Cardio Zone",
			"status": "Operational",
			"purchase_date": "2023-01-20",
			"purchase_price": 2800.00,
			"currency": "USD",
			"description": "Commercial grade elliptical trainer"
		},
		{
			"equipment_name": "Bench Press 001",
			"equipment_type": "Strength Training",
			"brand": "Hammer Strength",
			"model": "Pro Series",
			"location": "Weight Room",
			"status": "Operational",
			"purchase_date": "2023-02-01",
			"purchase_price": 1200.00,
			"currency": "USD",
			"description": "Professional bench press station"
		},
		{
			"equipment_name": "Dumbbell Set 001",
			"equipment_type": "Free Weights",
			"brand": "PowerBlock",
			"model": "Pro Series",
			"location": "Weight Room",
			"status": "Operational",
			"purchase_date": "2023-02-10",
			"purchase_price": 800.00,
			"currency": "USD",
			"description": "Adjustable dumbbell set 5-50 lbs"
		},
		{
			"equipment_name": "Yoga Mat 001",
			"equipment_type": "Accessories",
			"brand": "Manduka",
			"model": "Pro Series",
			"location": "Yoga Studio",
			"status": "Operational",
			"purchase_date": "2023-03-01",
			"purchase_price": 80.00,
			"currency": "USD",
			"description": "Premium yoga mat for classes"
		}
	]
	
	for equipment_data in equipment_list:
		if not frappe.db.exists("Gym Equipment", equipment_data["equipment_name"]):
			equipment = frappe.get_doc({
				"doctype": "Gym Equipment",
				**equipment_data
			})
			equipment.insert()


def create_sample_trainers():
	"""Create sample gym trainers"""
	
	trainers = [
		{
			"first_name": "John",
			"last_name": "Smith",
			"email": "john.smith@gym.com",
			"mobile_no": "+1234567890",
			"gender": "Male",
			"hire_date": "2023-01-01",
			"salary": 3500.00,
			"currency": "USD",
			"specialization": "Strength Training, Personal Training, CrossFit",
			"bio": "Certified personal trainer with 5+ years of experience in strength training and fitness coaching.",
			"certifications": [
				{"certification_name": "NASM-CPT", "issuing_organization": "NASM", "issue_date": "2022-06-01"},
				{"certification_name": "CrossFit Level 2", "issuing_organization": "CrossFit", "issue_date": "2022-08-15"}
			]
		},
		{
			"first_name": "Sarah",
			"last_name": "Johnson",
			"email": "sarah.johnson@gym.com",
			"mobile_no": "+1234567891",
			"gender": "Female",
			"hire_date": "2023-01-15",
			"salary": 3200.00,
			"currency": "USD",
			"specialization": "Yoga, Pilates, Group Fitness",
			"bio": "Experienced yoga and Pilates instructor with a focus on holistic wellness and mindfulness.",
			"certifications": [
				{"certification_name": "RYT-200", "issuing_organization": "Yoga Alliance", "issue_date": "2021-12-01"},
				{"certification_name": "Pilates Mat Certification", "issuing_organization": "PMA", "issue_date": "2022-03-01"}
			]
		},
		{
			"first_name": "Mike",
			"last_name": "Davis",
			"email": "mike.davis@gym.com",
			"mobile_no": "+1234567892",
			"gender": "Male",
			"hire_date": "2023-02-01",
			"salary": 3000.00,
			"currency": "USD",
			"specialization": "Cardio, HIIT, Group Classes",
			"bio": "High-energy fitness instructor specializing in cardio and HIIT workouts.",
			"certifications": [
				{"certification_name": "ACE Group Fitness", "issuing_organization": "ACE", "issue_date": "2022-09-01"},
				{"certification_name": "HIIT Certification", "issuing_organization": "HIIT Academy", "issue_date": "2022-11-01"}
			]
		}
	]
	
	for trainer_data in trainers:
		if not frappe.db.exists("Gym Trainer", {"email": trainer_data["email"]}):
			trainer = frappe.get_doc({
				"doctype": "Gym Trainer",
				**trainer_data
			})
			trainer.insert()


def create_sample_classes():
	"""Create sample gym classes"""
	
	classes = [
		{
			"class_name": "Morning Yoga",
			"class_type": "Yoga",
			"trainer": "Sarah Johnson",
			"max_capacity": 20,
			"duration_minutes": 60,
			"price": 15.00,
			"currency": "USD",
			"class_level": "All Levels",
			"description": "Gentle morning yoga class to start your day with mindfulness and flexibility.",
			"requirements": "Yoga mat, comfortable clothing",
			"benefits": "Improved flexibility, stress relief, better posture",
			"schedule": [
				{"day_of_week": "Monday", "start_time": "07:00:00", "end_time": "08:00:00", "is_active": 1},
				{"day_of_week": "Wednesday", "start_time": "07:00:00", "end_time": "08:00:00", "is_active": 1},
				{"day_of_week": "Friday", "start_time": "07:00:00", "end_time": "08:00:00", "is_active": 1}
			]
		},
		{
			"class_name": "Strength Training 101",
			"class_type": "Strength Training",
			"trainer": "John Smith",
			"max_capacity": 15,
			"duration_minutes": 45,
			"price": 20.00,
			"currency": "USD",
			"class_level": "Beginner",
			"description": "Introduction to strength training with proper form and technique.",
			"requirements": "Comfortable workout clothes, water bottle",
			"benefits": "Increased strength, muscle building, improved bone density",
			"schedule": [
				{"day_of_week": "Tuesday", "start_time": "18:00:00", "end_time": "18:45:00", "is_active": 1},
				{"day_of_week": "Thursday", "start_time": "18:00:00", "end_time": "18:45:00", "is_active": 1}
			]
		},
		{
			"class_name": "HIIT Cardio Blast",
			"class_type": "Cardio",
			"trainer": "Mike Davis",
			"max_capacity": 25,
			"duration_minutes": 30,
			"price": 12.00,
			"currency": "USD",
			"class_level": "Intermediate",
			"description": "High-intensity interval training for maximum calorie burn and cardiovascular fitness.",
			"requirements": "Comfortable workout clothes, towel, water bottle",
			"benefits": "Improved cardiovascular health, increased endurance, fat burning",
			"schedule": [
				{"day_of_week": "Monday", "start_time": "19:00:00", "end_time": "19:30:00", "is_active": 1},
				{"day_of_week": "Wednesday", "start_time": "19:00:00", "end_time": "19:30:00", "is_active": 1},
				{"day_of_week": "Friday", "start_time": "19:00:00", "end_time": "19:30:00", "is_active": 1}
			]
		}
	]
	
	for class_data in classes:
		if not frappe.db.exists("Gym Class", class_data["class_name"]):
			gym_class = frappe.get_doc({
				"doctype": "Gym Class",
				**class_data
			})
			gym_class.insert()


def create_sample_members():
	"""Create sample gym members"""
	
	members = [
		{
			"first_name": "Alice",
			"last_name": "Brown",
			"email": "alice.brown@email.com",
			"mobile_no": "+1234567893",
			"gender": "Female",
			"membership_plan": "Premium Monthly",
			"membership_start_date": "2024-01-01",
			"membership_end_date": "2024-02-01",
			"membership_status": "Active",
			"fitness_goals": "Weight loss, improved cardiovascular health",
			"health_conditions": "None",
			"allergies": "None"
		},
		{
			"first_name": "Bob",
			"last_name": "Wilson",
			"email": "bob.wilson@email.com",
			"mobile_no": "+1234567894",
			"gender": "Male",
			"membership_plan": "Basic Monthly",
			"membership_start_date": "2024-01-01",
			"membership_end_date": "2024-02-01",
			"membership_status": "Active",
			"fitness_goals": "Muscle building, strength training",
			"health_conditions": "None",
			"allergies": "None"
		},
		{
			"first_name": "Carol",
			"last_name": "Davis",
			"email": "carol.davis@email.com",
			"mobile_no": "+1234567895",
			"gender": "Female",
			"membership_plan": "VIP Monthly",
			"membership_start_date": "2024-01-01",
			"membership_end_date": "2024-02-01",
			"membership_status": "Active",
			"fitness_goals": "Overall fitness, stress relief, flexibility",
			"health_conditions": "Mild back pain",
			"allergies": "None"
		}
	]
	
	for member_data in members:
		if not frappe.db.exists("Gym Member", {"email": member_data["email"]}):
			member = frappe.get_doc({
				"doctype": "Gym Member",
				**member_data
			})
			member.insert()


def before_uninstall():
	"""Clean up data before uninstalling GMS"""
	# Add any cleanup logic here if needed
	pass
