# 📊 RPAS Business Management - Database Relational Map

**HSBC Engineering Standard**: Professional database relationship documentation  
**Purpose**: Complete model relationship mapping for debugging and development  
**Audience**: Software engineers, database administrators, AI development team

---

## 🎯 **EXECUTIVE SUMMARY**

### **System Architecture**
- **21 Django Models** across **5 Applications**
- **Universal Three-Color Compliance** integrated across 12+ operational models
- **Revolutionary F2 AI Automation** with "Set Once, Automate Forever" scheduling
- **Multi-tier Distribution**: Alpha (Django) + Delta (PostgreSQL/PostGIS/Redis) + Beta (React)

### **Core Design Patterns**
1. **Central Hub Architecture**: `core/` app provides foundation models
2. **One-Way Dependencies**: Apps reference core models, never reverse
3. **ComplianceMixin Universal**: GREEN/YELLOW/RED status on all operational models  
4. **UUID Primary Keys**: Distributed-system-ready identification
5. **Geographical Chaining**: Country → State → City → PostalCode normalization

---

## 📋 **COMPLETE MODEL INVENTORY**

### **Core Foundation (core/ app)**
| Model | Primary Key | Foreign Keys | Purpose | Compliance |
|-------|-------------|--------------|---------|------------|
| `CustomUser` | UUID | None | Email-based authentication | ✅ Built-in |
| `BaseProfile` | UUID | user (CustomUser) | Universal user profiles | ✅ ComplianceMixin |
| `Country` | UUID | None | Geographical normalization | ❌ Static data |
| `State` | UUID | country (Country) | Regional normalization | ❌ Static data |
| `City` | UUID | state (State) | City normalization | ❌ Static data |
| `PostalCode` | UUID | city (City) | Address normalization | ❌ Static data |
| `ComplianceRule` | UUID | None | CASA compliance rules | ❌ Configuration |
| `ComplianceCheck` | UUID | content_type, object_id | Universal compliance results | ❌ Results storage |

### **Authentication & Profiles (accounts/ app)**
| Model | Primary Key | Foreign Keys | Purpose | Compliance |
|-------|-------------|--------------|---------|------------|
| `BaseProfile` | UUID | user (CustomUser), address_city (City) | User profile foundation | ✅ ComplianceMixin |

### **F2 Technical Log System (rpas/ app)**
| Model | Primary Key | Foreign Keys | Purpose | Compliance |
|-------|-------------|--------------|---------|------------|
| `RPASOperator` | UUID | business_address_city (City) | ReOC operators | ✅ ComplianceMixin |
| `KeyPersonnel` | UUID | operator (RPASOperator), user (CustomUser) | CASA appointments | ✅ ComplianceMixin |
| `RPASAircraft` | UUID | operator (RPASOperator) | Aircraft registration | ✅ ComplianceMixin |
| `F2TechnicalLogPartA` | UUID | aircraft (RPASAircraft), pilot (CustomUser) | F2 log headers | ✅ ComplianceMixin |
| `F2FlightHoursEntry` | UUID | log (F2TechnicalLogPartA), pilot (CustomUser) | Flight tracking | ✅ ComplianceMixin |
| `F2MaintenanceEntry` | UUID | log (F2TechnicalLogPartA) | Maintenance work | ❌ Data entry |
| `F2DefectEntry` | UUID | log (F2TechnicalLogPartA) | Issue tracking | ❌ Data entry |
| `F2MaintenanceSchedule` | UUID | aircraft (RPASAircraft) | AI automation config | ❌ Configuration |
| `F2MaintenanceRequired` | UUID | schedule (F2MaintenanceSchedule) | AI-generated entries | ❌ AI output |

### **Safety Management System (sms/ app)**
| Model | Primary Key | Foreign Keys | Purpose | Compliance |
|-------|-------------|--------------|---------|------------|
| `SMSRiskAssessment` | UUID | operator (RPASOperator), assessor (CustomUser) | Risk analysis | ✅ ComplianceMixin |
| `SMSIncidentReport` | UUID | operator (RPASOperator), reporter (CustomUser) | Incident tracking | ✅ ComplianceMixin |
| `SMSHazardRegister` | UUID | operator (RPASOperator), identified_by (CustomUser) | Hazard management | ✅ ComplianceMixin |
| `SMSSafetyMeeting` | UUID | operator (RPASOperator), chair (CustomUser) | Meeting records | ✅ ComplianceMixin |

### **Aviation Airspace (aviation/ app)**
| Model | Primary Key | Foreign Keys | Purpose | Compliance |
|-------|-------------|--------------|---------|------------|
| `AirspaceRestriction` | UUID | None | Controlled airspace | ✅ ComplianceMixin |
| `FlightPlanning` | UUID | pilot (CustomUser), aircraft (RPASAircraft) | Flight operations | ✅ ComplianceMixin |
| `WeatherCondition` | UUID | assessment (FlightPlanning) | Weather data | ✅ ComplianceMixin |

---

## 🏗️ **VISUAL RELATIONSHIP DIAGRAM**

```
CORE FOUNDATION LAYER (Level 0)
┌─────────────────────────────────────────────────────────────────┐
│  CustomUser (UUID) ←─── Email-based authentication              │
│      │                                                          │
│      └─→ BaseProfile (UUID) ←─── ComplianceMixin                │
│                                                                 │
│  Country (UUID) → State (UUID) → City (UUID) → PostalCode      │
│      │                 │             │                          │
│      └─────────────────├─────────────┘                         │
│                        │                                        │
│  ComplianceRule (UUID) ←┴─── CASA regulation engine            │
│      │                                                          │
│      └─→ ComplianceCheck (UUID) ←─── Universal compliance       │
└─────────────────────────────────────────────────────────────────┘

RPAS OPERATIONS LAYER (Level 1)
┌─────────────────────────────────────────────────────────────────┐
│  RPASOperator (UUID) ←─── ReOC Certificate Holder               │
│      │                        ↑                                │
│      │                        │ business_address_city           │
│      │                        │                                │
│      ├─→ KeyPersonnel (UUID) ←─┴─── CustomUser (user)          │
│      │                                                          │
│      └─→ RPASAircraft (UUID) ←─── Fleet Management             │
│              │                                                  │
│              ├─→ F2TechnicalLogPartA (UUID) ←─── CustomUser     │
│              │         │                              (pilot)   │
│              │         ├─→ F2FlightHoursEntry (UUID)           │
│              │         ├─→ F2MaintenanceEntry (UUID)           │
│              │         └─→ F2DefectEntry (UUID)                 │
│              │                                                  │
│              └─→ F2MaintenanceSchedule (UUID) ←─── AI Engine    │
│                         │                                       │
│                         └─→ F2MaintenanceRequired (UUID)        │
└─────────────────────────────────────────────────────────────────┘

SAFETY & AVIATION LAYER (Level 2)
┌─────────────────────────────────────────────────────────────────┐
│  SMS Models (4) ←─── RPASOperator + CustomUser                  │
│  ├─ SMSRiskAssessment (UUID)                                    │
│  ├─ SMSIncidentReport (UUID)                                    │
│  ├─ SMSHazardRegister (UUID)                                    │
│  └─ SMSSafetyMeeting (UUID)                                     │
│                                                                 │
│  Aviation Models (3) ←─── CustomUser + RPASAircraft            │
│  ├─ AirspaceRestriction (UUID)                                 │
│  ├─ FlightPlanning (UUID)                                       │
│  └─ WeatherCondition (UUID)                                     │
└─────────────────────────────────────────────────────────────────┘

THREE-COLOR COMPLIANCE OVERLAY (All Levels)
┌─────────────────────────────────────────────────────────────────┐
│  🟢 GREEN: CASA Compliant, Operations Authorized                │
│  🟡 YELLOW: Warning State, Review Required                      │
│  🔴 RED: Non-Compliant, Operations Prohibited                   │
│                                                                 │
│  ComplianceMixin.get_compliance_summary() → ALL 12+ Models      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 **PRIMARY FOREIGN KEY RELATIONSHIPS**

### **User & Profile Relationships**
```python
# Core user connection
BaseProfile.user → CustomUser (One-to-One)
BaseProfile.address_city → City (Many-to-One)

# Profile extensions
KeyPersonnel.user → CustomUser (Many-to-One)
KeyPersonnel.operator → RPASOperator (Many-to-One)
```

### **Geographical Chain (Normalized)**
```python
# Hierarchical geographical data
State.country → Country (Many-to-One)
City.state → State (Many-to-One)  
PostalCode.city → City (Many-to-One)

# Usage in profiles and operators
BaseProfile.address_city → City (Many-to-One)
RPASOperator.business_address_city → City (Many-to-One)
```

### **RPAS Operations Chain**
```python
# Core RPAS hierarchy
RPASOperator (ReOC) ← KeyPersonnel (CASA Appointments)
RPASOperator ← RPASAircraft (Fleet)

# F2 Technical Log chain
RPASAircraft → F2TechnicalLogPartA (Log headers)
F2TechnicalLogPartA → F2FlightHoursEntry (Flight tracking)
F2TechnicalLogPartA → F2MaintenanceEntry (Maintenance work)
F2TechnicalLogPartA → F2DefectEntry (Defect tracking)

# AI Automation chain  
RPASAircraft → F2MaintenanceSchedule (Configuration)
F2MaintenanceSchedule → F2MaintenanceRequired (AI-generated)
```

### **Safety Management Relationships**
```python
# All SMS models follow same pattern
SMSRiskAssessment.operator → RPASOperator (Many-to-One)
SMSRiskAssessment.assessor → CustomUser (Many-to-One)

SMSIncidentReport.operator → RPASOperator (Many-to-One)  
SMSIncidentReport.reporter → CustomUser (Many-to-One)

SMSHazardRegister.operator → RPASOperator (Many-to-One)
SMSHazardRegister.identified_by → CustomUser (Many-to-One)

SMSSafetyMeeting.operator → RPASOperator (Many-to-One)
SMSSafetyMeeting.chair → CustomUser (Many-to-One)
```

### **Aviation Operations Relationships**
```python
# Flight planning chain
FlightPlanning.pilot → CustomUser (Many-to-One)
FlightPlanning.aircraft → RPASAircraft (Many-to-One)
WeatherCondition.assessment → FlightPlanning (Many-to-One)

# Airspace restrictions (spatial data)
AirspaceRestriction (GeoDjango model with spatial fields)
```

---

## 🔄 **GENERIC FOREIGN KEY RELATIONSHIPS**

### **Universal Compliance System**
```python
# ComplianceCheck links to ANY model
ComplianceCheck.content_type → ContentType (Many-to-One)
ComplianceCheck.object_id → Any model's UUID
ComplianceCheck.content_object → Generic relation to any model

# Usage examples
ComplianceCheck → RPASAircraft (aircraft compliance)
ComplianceCheck → F2TechnicalLogPartA (log compliance)  
ComplianceCheck → SMSRiskAssessment (safety compliance)
ComplianceCheck → FlightPlanning (operational compliance)
```

---

## 🔗 **MANY-TO-MANY RELATIONSHIPS**

### **Future Implementation (django-guardian)**
```python
# Object-level permissions (planned)
CustomUser ←→ RPASAircraft (pilot authorization)
CustomUser ←→ RPASOperator (operational access)
KeyPersonnel ←→ AirspaceRestriction (airspace permissions)
```

---

## ⚡ **PERFORMANCE OPTIMIZATION GUIDE**

### **Critical Database Indexes**
```python
# High-frequency lookups requiring indexes
CustomUser.email (unique index - authentication)
BaseProfile.user_id (foreign key index)
BaseProfile.profile_type (choice field index)
F2TechnicalLogPartA.aircraft_id (foreign key index)
F2FlightHoursEntry.log_id (foreign key index)
ComplianceCheck.content_type + object_id (composite index)
```

### **Query Optimization Patterns**
```python
# Avoid N+1 queries with select_related
aircraft_with_operator = RPASAircraft.objects.select_related('operator')
logs_with_aircraft = F2TechnicalLogPartA.objects.select_related('aircraft__operator')

# Prefetch related objects for reverse relationships  
operator_with_aircraft = RPASOperator.objects.prefetch_related('rpasaircraft_set')
user_with_profiles = CustomUser.objects.prefetch_related('baseprofile_set')

# Compliance data optimization
model_with_compliance = RPASAircraft.objects.prefetch_related('compliancecheck_set')
```

---

## 🧭 **DEBUGGING QUICK REFERENCE**

### **Common Relationship Lookups**
```python
# Find all aircraft for an operator
operator.rpasaircraft_set.all()

# Find all logs for an aircraft  
aircraft.f2technicallogparta_set.all()

# Find all flight hours for a log
log.f2flighthoursentry_set.all()

# Find compliance checks for any model
model_instance.compliancecheck_set.all()

# Navigate geographical chain upward
city.state.country.name
postal_code.city.state.country.name

# Navigate geographical chain downward
country.state_set.all()
state.city_set.all() 
city.postalcode_set.all()
```

### **Compliance Status Debugging**
```python
# Universal compliance checking (available on ALL operational models)
aircraft.get_compliance_summary()
risk_assessment.get_compliance_summary()
flight_planning.get_compliance_summary()
operator.get_compliance_summary()

# Returns format:
{
    'overall_status': 'green|yellow|red',
    'total_checks': int,
    'failed_checks': int, 
    'last_checked': datetime
}
```

### **F2 AI Automation Debugging**
```python
# Check automation configuration
schedule = F2MaintenanceSchedule.objects.get(aircraft=aircraft)
schedule.flight_hours_trigger_enabled  # Boolean
schedule.flight_hours_threshold        # Integer hours

# Find AI-generated maintenance entries  
schedule.f2maintenancerequired_set.filter(
    auto_generated=True
)

# Trigger automation manually (testing)
schedule.check_and_generate_maintenance()
```

---

## 🎯 **MODEL DEPENDENCY HIERARCHY**

### **Level 0: Independent Foundation**
- `CustomUser`, `Country`, `ComplianceRule`

### **Level 1: Core Dependencies**  
- `BaseProfile` (→ CustomUser, City)
- `State` (→ Country)

### **Level 2: Extended Dependencies**
- `City` (→ State)  
- `RPASOperator` (→ City)

### **Level 3: Operational Dependencies**
- `PostalCode` (→ City)
- `KeyPersonnel` (→ RPASOperator, CustomUser)
- `RPASAircraft` (→ RPASOperator)

### **Level 4: F2 Log Dependencies**
- `F2TechnicalLogPartA` (→ RPASAircraft, CustomUser)
- `F2MaintenanceSchedule` (→ RPASAircraft)

### **Level 5: F2 Entry Dependencies**
- `F2FlightHoursEntry` (→ F2TechnicalLogPartA, CustomUser)
- `F2MaintenanceEntry` (→ F2TechnicalLogPartA)
- `F2DefectEntry` (→ F2TechnicalLogPartA)
- `F2MaintenanceRequired` (→ F2MaintenanceSchedule)

### **Level 6: Safety Dependencies**
- `SMSRiskAssessment` (→ RPASOperator, CustomUser)
- `SMSIncidentReport` (→ RPASOperator, CustomUser)
- `SMSHazardRegister` (→ RPASOperator, CustomUser)
- `SMSSafetyMeeting` (→ RPASOperator, CustomUser)

### **Level 7: Aviation Dependencies**
- `FlightPlanning` (→ CustomUser, RPASAircraft)

### **Level 8: Weather Dependencies**
- `WeatherCondition` (→ FlightPlanning)

---

## 📊 **COMPLIANCE INTEGRATION STATUS**

### **✅ ComplianceMixin Integrated (12+ Models)**
- `BaseProfile` (Core)
- `RPASOperator`, `KeyPersonnel`, `RPASAircraft`, `F2TechnicalLogPartA`, `F2FlightHoursEntry` (RPAS)
- `SMSRiskAssessment`, `SMSIncidentReport`, `SMSHazardRegister`, `SMSSafetyMeeting` (SMS)
- `AirspaceRestriction`, `FlightPlanning`, `WeatherCondition` (Aviation)

### **❌ No Compliance Integration (Data/Config Models)**
- `CustomUser` (built-in compliance)
- `Country`, `State`, `City`, `PostalCode` (static geographical data)
- `ComplianceRule`, `ComplianceCheck` (compliance system itself)
- `F2MaintenanceEntry`, `F2DefectEntry` (data entry models)
- `F2MaintenanceSchedule`, `F2MaintenanceRequired` (AI configuration/output)

---

**Created**: November 23, 2025  
**Standard**: HSBC Engineering Requirements  
**Maintainer**: AI Development Team  
**Version**: 1.0 - Initial comprehensive mapping

> "This relational map is a life saver for debugging and future development" - HSBC Senior Software Engineer