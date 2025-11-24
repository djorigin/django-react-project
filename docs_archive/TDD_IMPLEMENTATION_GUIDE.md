# Test Driven Development Guide for RPAS Compliance System

## 🎯 TDD Philosophy: "TEST FIRST THEN CODE"

**REVOLUTIONARY DEVELOPMENT SHIFT**: From "code first" to **Test Driven Development** with the RED-GREEN-REFACTOR cycle.

### The TDD Mantra
```
RED → GREEN → REFACTOR
1. Write a failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor and improve (REFACTOR)
```

## 🚁 Aviation-Specific TDD Implementation

### Core TDD Principles for CASA Compliance
- **Safety First**: All aviation features must have comprehensive test coverage
- **Compliance Driven**: Tests should verify CASA regulatory requirements
- **Real-World Scenarios**: Use realistic aviation data in tests
- **Performance Conscious**: Aviation operations require fast response times

## 📋 TDD Framework Stack

### Selected Frameworks (Analysis Score: 95/100)
```toml
# Core TDD packages - INSTALLED ✅
pytest-django==4.8.0      # Superior Django integration
factory-boy==3.3.1        # Realistic test data generation  
pytest-mock==3.12.0       # Advanced mocking capabilities
coverage==7.4.0           # Code coverage analysis
pytest-cov==4.1.0         # Pytest coverage integration

# Browser Testing - PENDING INSTALL
playwright==1.41.0        # Modern browser automation (94/100)
```

### Framework Justification
- **pytest-django** over unittest: Better fixtures, parametrization, cleaner syntax
- **factory-boy** over manual data: Realistic aviation data generation
- **Playwright** over Selenium: Modern, faster, better HTMX support
- **Coverage.py**: Industry standard with 85% minimum threshold

## 🧪 Test Organization Structure

```
tests/
├── __init__.py                    # Test package initialization
├── factories.py                  # ✅ Aviation test data factories
├── test_compliance_system.py     # ✅ Core compliance system tests
├── conftest.py                   # Pytest configuration and fixtures
├── unit/                         # Unit tests for individual components
│   ├── test_models.py            # Django model unit tests
│   ├── test_forms.py             # Form validation tests
│   ├── test_views.py             # View logic tests
│   └── test_services.py          # Business logic service tests
├── integration/                  # Integration tests for workflows
│   ├── test_compliance_workflow.py
│   ├── test_f2_automation.py    # F2 technical log automation
│   └── test_user_registration.py
├── browser/                      # End-to-end browser tests
│   ├── test_compliance_ui.py    # Three-color compliance UI
│   ├── test_htmx_interactions.py
│   └── test_mobile_responsive.py
└── performance/                  # Performance and load tests
    ├── test_compliance_performance.py
    └── test_database_queries.py
```

## 🎯 TDD Markers and Categories

```python
# Test markers for organization
@pytest.mark.unit           # Unit tests - fast, isolated
@pytest.mark.integration    # Integration tests - multiple components
@pytest.mark.compliance     # CASA compliance rule tests
@pytest.mark.browser        # Browser/E2E tests - slow
@pytest.mark.slow          # Tests taking >2 seconds
@pytest.mark.api           # API endpoint tests
@pytest.mark.model         # Django model tests
@pytest.mark.form          # Django form tests
@pytest.mark.view          # Django view tests
@pytest.mark.aviation      # Aviation-specific business logic
@pytest.mark.f2            # F2 Technical Log tests
@pytest.mark.sms           # Safety Management System tests
@pytest.mark.geographical  # Geographical data tests
@pytest.mark.profile       # User profile tests
```

## 🔬 TDD Test Examples

### 1. RED Phase: Write Failing Test
```python
def test_pilot_arn_validation_fails_without_arn():
    """RED: Test that pilot profile requires ARN number."""
    # This test should FAIL initially
    pilot_profile = PilotProfileFactory(user__arn_number=None)
    
    compliance_summary = pilot_profile.get_compliance_summary()
    
    # This assertion should FAIL (RED)
    assert compliance_summary['overall_status'] == 'red'
    assert 'ARN required' in compliance_summary['failed_checks'][0]['message']
```

### 2. GREEN Phase: Minimal Implementation
```python
# In core/models.py - Add minimal code to pass test
class ComplianceRule(models.Model):
    def evaluate_against_object(self, obj):
        if self.field_path == 'user.arn_number':
            if not getattr(obj.user, 'arn_number'):
                return {
                    'status': 'red', 
                    'message': 'ARN required'
                }
        return {'status': 'green'}
```

### 3. REFACTOR Phase: Improve Implementation
```python
# Refactor to robust, reusable solution
class ComplianceRule(models.Model):
    def evaluate_against_object(self, obj):
        # Full evaluation logic with all 13 evaluation types
        field_value = self._get_field_value(obj, self.field_path)
        
        if self.evaluation_type == 'exists':
            return self._evaluate_exists(field_value)
        # ... additional evaluation types
```

## 🎪 Factory Pattern for Aviation Data

### Realistic Test Data Generation
```python
# Use factory-boy for realistic aviation data
class PilotProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BaseProfile
    
    profile_type = 'pilot'
    user = factory.SubFactory(PilotUserFactory)
    
    # Realistic aviation data
    casa_certificate_number = factory.LazyFunction(
        lambda: f"RePL-{fake.random_number(digits=6)}"
    )
    certificate_expiry_date = factory.LazyFunction(
        lambda: timezone.now().date() + timedelta(days=365)
    )
    
    # Aviation Reference Number
    user__arn_number = factory.LazyFunction(
        lambda: f"RPC{fake.random_number(digits=6)}"
    )
```

### Aviation Data Generator Utilities
```python
class AviationDataGenerator:
    @staticmethod
    def generate_aircraft_registration():
        return f"VH-{fake.lexify('????').upper()}"
    
    @staticmethod 
    def generate_flight_hours():
        return Decimal(str(round(fake.random.uniform(0.1, 500.0), 1)))
```

## 🚦 Coverage Requirements

### Minimum Coverage Thresholds
```toml
[tool.coverage.report]
# Aviation safety requires high test coverage
fail_under = 85  # Minimum 85% coverage
show_missing = true
skip_covered = false
```

### Coverage by Component
- **Core Models**: 95%+ (safety-critical)
- **Compliance Engine**: 100% (regulatory requirements)
- **F2 Automation**: 90%+ (technical log accuracy)
- **Views/Forms**: 80%+ (user interface reliability)
- **Utilities**: 85%+ (supporting functions)

## 🎯 TDD Workflow Commands

### Development Workflow
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python3 -m pytest

# Run specific test categories
python3 -m pytest -m compliance        # Compliance tests only
python3 -m pytest -m "unit and model"  # Unit tests for models
python3 -m pytest -m "not slow"        # Skip slow tests

# Run with coverage
python3 -m pytest --cov=. --cov-report=html

# Run specific test file
python3 -m pytest tests/test_compliance_system.py

# Run single test
python3 -m pytest tests/test_compliance_system.py::TestComplianceRuleEvaluation::test_date_past_evaluation_fails_for_expired_certificate

# Verbose output for debugging
python3 -m pytest -v --tb=long

# Watch mode for continuous testing (requires pytest-watch)
ptw -- -m "not slow"
```

### TDD Red-Green-Refactor Cycle
```bash
# 1. RED: Write failing test
python3 -m pytest tests/test_new_feature.py -v
# Expected: Test fails ❌

# 2. GREEN: Write minimal code
# Edit source code...
python3 -m pytest tests/test_new_feature.py -v
# Expected: Test passes ✅

# 3. REFACTOR: Improve code
python3 -m pytest tests/test_new_feature.py -v
# Expected: Test still passes ✅ with better code

# 4. Run full suite
python3 -m pytest --cov=. 
# Expected: All tests pass ✅ with good coverage
```

## 🎪 Aviation-Specific TDD Scenarios

### CASA Compliance Testing
```python
class TestCASACompliance:
    """Aviation regulatory compliance tests."""
    
    def test_pilot_currency_requirements(self):
        """Test CASA pilot currency validation."""
        # RED: Should fail for expired currency
        
    def test_aircraft_registration_validity(self):
        """Test aircraft registration compliance."""
        # GREEN: Should pass for valid registration
        
    def test_maintenance_schedule_adherence(self):
        """Test maintenance interval compliance."""
        # REFACTOR: Optimize maintenance checking logic
```

### F2 Technical Log Automation Testing
```python
class TestF2Automation:
    """F2 technical log automation tests."""
    
    def test_autonomous_maintenance_generation(self):
        """Test AI generates F2MaintenanceRequired automatically."""
        
    def test_flight_hours_threshold_detection(self):
        """Test system detects flight hours thresholds."""
        
    def test_calendar_based_maintenance_triggers(self):
        """Test calendar-based maintenance scheduling."""
```

### Three-Color Compliance UI Testing
```python
class TestComplianceUI:
    """Browser tests for three-color compliance system."""
    
    def test_red_status_visual_feedback(self):
        """Test RED compliance status displays correctly."""
        
    def test_htmx_real_time_compliance_updates(self):
        """Test HTMX provides real-time compliance feedback."""
        
    def test_mobile_responsive_compliance_display(self):
        """Test compliance status on mobile devices."""
```

## 🎯 TDD Best Practices for Aviation Systems

### 1. Safety-First Testing
- **Critical Path Coverage**: 100% coverage for safety-critical functions
- **Edge Case Testing**: Test boundary conditions and error scenarios
- **Regulatory Compliance**: Verify CASA rule adherence in tests

### 2. Realistic Test Data
- **Factory Patterns**: Use factory-boy for consistent test data
- **Aviation Standards**: Generate data matching industry patterns
- **Boundary Testing**: Test with edge case values (expiry dates, limits)

### 3. Performance Testing
- **Response Time**: Aviation operations need fast response (<2 seconds)
- **Database Efficiency**: Test query optimization and N+1 problems
- **Concurrent Access**: Test multiple user scenarios

### 4. Integration Testing  
- **End-to-End Workflows**: Test complete user journeys
- **External Dependencies**: Mock CASA APIs and external services
- **Browser Compatibility**: Test across devices and browsers

## 📊 TDD Metrics and Monitoring

### Code Quality Metrics
```bash
# Coverage report
python3 -m pytest --cov=. --cov-report=term-missing

# Performance profiling
python3 -m pytest --profile

# Test timing
python3 -m pytest --durations=10
```

### Success Criteria
- **Test Coverage**: >85% overall, >95% for safety-critical code
- **Test Speed**: Unit tests <1s, Integration tests <10s
- **Test Reliability**: >99% pass rate in CI/CD
- **Maintenance**: Tests updated with feature changes

## 🚀 Next Steps: TDD Implementation

### Phase 1: Foundation Setup ✅
- ✅ Install TDD framework stack
- ✅ Configure pytest and coverage
- ✅ Create test structure and factories
- ✅ Write initial compliance system tests

### Phase 2: Comprehensive Test Suite
- [ ] Create unit tests for all models
- [ ] Add integration tests for workflows  
- [ ] Implement browser tests with Playwright
- [ ] Add performance and load tests

### Phase 3: Advanced TDD Integration
- [ ] Implement watch mode for continuous testing
- [ ] Add property-based testing with Hypothesis
- [ ] Create mutation testing for test quality
- [ ] Integrate with CI/CD pipeline

## 📚 Additional Resources

### TDD Learning Resources
- **Test-Driven Development by Example** - Kent Beck
- **Clean Code: Chapter 9 Unit Tests** - Robert Martin  
- **Effective Testing with pytest** - Brian Okken

### Django TDD Resources
- **Django Testing Documentation**: https://docs.djangoproject.com/en/5.2/topics/testing/
- **pytest-django Documentation**: https://pytest-django.readthedocs.io/
- **Factory Boy Documentation**: https://factoryboy.readthedocs.io/

### Aviation Testing Standards
- **CASA Guidelines**: Civil Aviation Safety Authority testing requirements
- **ISO 9001**: Quality management systems for aviation
- **DO-178C**: Software considerations in airborne systems

---

**Remember: "TEST FIRST THEN CODE" - Revolutionary development thinking for aviation safety! ✈️**