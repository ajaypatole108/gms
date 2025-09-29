### Core Features
- **Member Management**: Complete member profiles, membership tracking, and visit history
- **Membership Plans**: Flexible membership plans with different tiers and pricing
- **Equipment Management**: Track gym equipment, maintenance schedules, and usage
- **Class Scheduling**: Manage group classes, trainers, and bookings
- **Visit Tracking**: Check-in/check-out system with detailed visit logs


## DocTypes

### Core DocTypes
1. **Gym Member** - Member profiles and information
2. **Gym Membership Plan** - Membership plans and pricing
3. **Gym Equipment** - Equipment inventory and maintenance
4. **Gym Trainer** - Trainer profiles and schedules
5. **Gym Class** - Class definitions and schedules
6. **Gym Visit** - Member visit tracking
7. **Gym Class Booking** - Class booking management

### Supporting DocTypes
- **Gym Membership Plan Feature** - Plan features and benefits
- **Gym Class Schedule** - Class timing and availability
- **Gym Trainer Certification** - Trainer qualifications
- **Gym Trainer Working Hours** - Trainer availability
- **Gym Equipment Maintenance** - Maintenance tracking
- **Gym Visit Equipment** - Equipment usage during visits


### Installation Steps

1. **Clone the repository**:
```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/your-repo/gms --branch develop
```

2. **Install the app**:
```bash
bench install-app gms
```

3. **Migrate the database**:
```bash
bench migrate
```

4. **Restart the server**:
```bash
bench restart
```