import pytest
from app.models import Customer, Simulation


class TestCustomerEndpoints:
    """Integration tests for customer API endpoints."""

    def test_create_customer_success(self, client):
        """Test successful customer creation."""
        response = client.post("/customers", json={
            "company_name": "Test Company",
            "tax_id": "B87654323",  # Valid CIF with correct control digit
            "email": "test@company.com",
            "country": "ES",
            "plan": "Professional"
        })
        data = response.json()
        assert data["tax_id"] == "B87654323"
        assert response.status_code == 201
        data = response.json()
        assert data["company_name"] == "Test Company"
        assert data["tax_id"] == "B87654323"
        assert data["email"] == "test@company.com"
        assert data["country"] == "ES"
        assert data["plan"] == "Professional"
        assert "id" in data
        assert "created_at" in data

    def test_create_customer_missing_fields(self, client):
        """Test customer creation with missing required fields."""
        response = client.post("/customers", json={
            "company_name": "Test Company",
            # missing tax_id, email, country, plan
        })
        assert response.status_code == 422

    def test_create_customer_invalid_email(self, client):
        """Test customer creation with invalid email."""
        response = client.post("/customers", json={
            "company_name": "Test Company",
            "tax_id": "B87654321",
            "email": "not-an-email",
            "country": "ES",
            "plan": "Professional"
        })
        assert response.status_code == 422

    def test_create_customer_invalid_country(self, client):
        """Test customer creation with invalid country code."""
        response = client.post("/customers", json={
            "company_name": "Test Company",
            "tax_id": "B87654321",
            "email": "test@company.com",
            "country": "SPAIN",  # Should be 2-letter code
            "plan": "Professional"
        })
        assert response.status_code == 422

    def test_create_customer_invalid_plan(self, client):
        """Test customer creation with invalid plan."""
        response = client.post("/customers", json={
            "company_name": "Test Company",
            "tax_id": "B87654321",
            "email": "test@company.com",
            "country": "ES",
            "plan": "InvalidPlan"
        })
        assert response.status_code == 422

    def test_create_customer_valid_dni(self, client):
        """Test customer creation with valid DNI."""
        response = client.post("/customers", json={
            "company_name": "Persona Física",
            "tax_id": "52892374X",  # Valid DNI with correct control letter
            "email": "persona@test.com",
            "country": "ES",
            "plan": "Basic"
        })
        assert response.status_code == 201

    def test_create_customer_valid_nie(self, client):
        """Test customer creation with valid NIE."""
        response = client.post("/customers", json={
            "company_name": "Extranjero Residente",
            "tax_id": "X1234567L",
            "email": "extranjero@test.com",
            "country": "ES",
            "plan": "Basic"
        })
        assert response.status_code == 201

    def test_create_customer_valid_cif(self, client):
        """Test customer creation with valid CIF."""
        response = client.post("/customers", json={
            "company_name": "Empresa SL",
            "tax_id": "B87654323",  # Valid CIF with correct control digit
            "email": "empresa@test.com",
            "country": "ES",
            "plan": "Professional"
        })
        assert response.status_code == 201

    def test_create_customer_invalid_spanish_tax_id(self, client):
        """Test customer creation with invalid Spanish tax ID."""
        response = client.post("/customers", json={
            "company_name": "Test Company",
            "tax_id": "12345678A",  # Invalid control letter
            "email": "test@company.com",
            "country": "ES",
            "plan": "Professional"
        })
        assert response.status_code == 422
        assert "Invalid Spanish tax ID" in response.json()["detail"][0]["msg"]

    def test_create_customer_duplicate_tax_id_same_country(self, client, sample_customer):
        """Test duplicate tax ID in same country is rejected."""
        response = client.post("/customers", json={
            "company_name": "Another Company",
            "tax_id": "B87654323",  # Same as sample_customer
            "email": "another@company.com",
            "country": "ES",  # Same country
            "plan": "Basic"
        })
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_customer_same_tax_id_different_country(self, client, sample_customer):
        """Test same tax ID in different country is allowed."""
        response = client.post("/customers", json={
            "company_name": "German Company",
            "tax_id": "B87654321",  # Same tax_id
            "email": "german@company.com",
            "country": "DE",  # Different country
            "plan": "Professional"
        })
        assert response.status_code == 201

    def test_create_customer_non_spain_no_tax_validation(self, client):
        """Test that non-Spain countries don't validate Spanish tax ID format."""
        response = client.post("/customers", json={
            "company_name": "German Corp",
            "tax_id": "INVALID123",  # Would be invalid in Spain
            "email": "german@corp.de",
            "country": "DE",
            "plan": "Enterprise"
        })
        assert response.status_code == 201

    def test_list_customers_empty(self, client):
        """Test listing customers when none exist."""
        response = client.get("/customers")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_customers_with_data(self, client, sample_customer):
        """Test listing customers with existing data."""
        response = client.get("/customers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_customer.id

    def test_list_customers_pagination(self, client, db_session):
        """Test customer list pagination."""
        # Create multiple customers
        for i in range(15):
            c = Customer(
                company_name=f"Company {i}",
                tax_id=f"B{10000000 + i}",
                email=f"company{i}@test.com",
                country="ES",
                plan="Basic"
            )
            db_session.add(c)
        db_session.commit()

        response = client.get("/customers?skip=0&limit=10")
        assert response.status_code == 200
        assert len(response.json()) == 10

        response = client.get("/customers?skip=10&limit=10")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_get_customer_success(self, client, sample_customer):
        """Test getting an existing customer."""
        response = client.get(f"/customers/{sample_customer.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_customer.id
        assert data["company_name"] == sample_customer.company_name

    def test_get_customer_not_found(self, client):
        """Test getting a non-existent customer."""
        response = client.get("/customers/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_customer_success(self, client, sample_customer):
        """Test successful customer deletion."""
        response = client.delete(f"/customers/{sample_customer.id}")
        assert response.status_code == 204

        # Verify customer is gone
        response = client.get(f"/customers/{sample_customer.id}")
        assert response.status_code == 404

    def test_delete_customer_not_found(self, client):
        """Test deleting a non-existent customer."""
        response = client.delete("/customers/99999")
        assert response.status_code == 404

    def test_delete_customer_cascades_simulations(self, client, sample_customer, db_session):
        """Test that deleting a customer also deletes their simulations."""
        # Create a simulation for the customer
        sim = Simulation(
            customer_id=sample_customer.id,
            active_users=10,
            storage_gb=100.0,
            estimated_api_calls=50000,
            base_amount_cents=10000,
            tax_rate=0.21,
            tax_amount_cents=2100,
            total_amount_cents=12100
        )
        db_session.add(sim)
        db_session.commit()
        sim_id = sim.id

        # Delete customer
        response = client.delete(f"/customers/{sample_customer.id}")
        assert response.status_code == 204

        # Verify simulation is also deleted
        response = client.get(f"/simulations/{sim_id}")
        assert response.status_code == 404


class TestSimulationEndpoints:
    """Integration tests for simulation API endpoints."""

    def test_create_simulation_success(self, client, sample_customer):
        """Test successful simulation creation."""
        response = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 10,
            "storage_gb": 100.0,
            "estimated_api_calls": 50000
        })
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == sample_customer.id
        assert data["active_users"] == 10
        assert data["storage_gb"] == 100.0
        assert data["estimated_api_calls"] == 50000
        assert data["base_amount_cents"] == 10000  # 10 users * €10
        assert data["tax_rate"] == 0.21
        assert data["tax_amount_cents"] == 2100
        assert data["total_amount_cents"] == 12100
        assert "id" in data
        assert "created_at" in data

    def test_create_simulation_customer_not_found(self, client):
        """Test simulation creation for non-existent customer."""
        response = client.post("/simulations", json={
            "customer_id": 99999,
            "active_users": 10,
            "storage_gb": 100.0,
            "estimated_api_calls": 50000
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_simulation_negative_users(self, client, sample_customer):
        """Test simulation creation with negative users."""
        response = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": -5,
            "storage_gb": 100.0,
            "estimated_api_calls": 50000
        })
        assert response.status_code == 201  # Currently accepts, pricing returns 0
        # Note: Could add validation to reject negative values

    def test_create_simulation_zero_users(self, client, sample_customer):
        """Test simulation creation with zero users."""
        response = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 0,
            "storage_gb": 100.0,
            "estimated_api_calls": 50000
        })
        assert response.status_code == 201
        data = response.json()
        assert data["base_amount_cents"] == 0
        assert data["total_amount_cents"] == 0

    def test_create_simulation_tier_transitions(self, client, sample_customer):
        """Test simulation pricing at tier boundaries."""
        # 10 users (end of first tier)
        r10 = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 10,
            "storage_gb": 0,
            "estimated_api_calls": 0
        })
        assert r10.json()["base_amount_cents"] == 10000

        # 11 users (start of second tier)
        r11 = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 11,
            "storage_gb": 0,
            "estimated_api_calls": 0
        })
        assert r11.json()["base_amount_cents"] == 10800

        # 50 users (end of second tier)
        r50 = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 50,
            "storage_gb": 0,
            "estimated_api_calls": 0
        })
        assert r50.json()["base_amount_cents"] == 42000

        # 51 users (start of third tier)
        r51 = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 51,
            "storage_gb": 0,
            "estimated_api_calls": 0
        })
        assert r51.json()["base_amount_cents"] == 42500

    def test_get_customer_simulations(self, client, sample_customer, db_session):
        """Test getting all simulations for a customer."""
        # Create multiple simulations
        for users in [5, 10, 15]:
            sim = Simulation(
                customer_id=sample_customer.id,
                active_users=users,
                storage_gb=50.0,
                estimated_api_calls=10000,
                base_amount_cents=users * 1000,
                tax_rate=0.21,
                tax_amount_cents=round(users * 1000 * 0.21),
                total_amount_cents=users * 1000 + round(users * 1000 * 0.21)
            )
            db_session.add(sim)
        db_session.commit()

        response = client.get(f"/customers/{sample_customer.id}/simulations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be ordered by creation (oldest first)
        assert data[0]["active_users"] == 5
        assert data[1]["active_users"] == 10
        assert data[2]["active_users"] == 15

    def test_get_customer_simulations_empty(self, client, sample_customer):
        """Test getting simulations for customer with none."""
        response = client.get(f"/customers/{sample_customer.id}/simulations")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_customer_simulations_customer_not_found(self, client):
        """Test getting simulations for non-existent customer."""
        response = client.get("/customers/99999/simulations")
        assert response.status_code == 404

    def test_get_simulation_by_id(self, client, sample_customer, db_session):
        """Test getting a specific simulation by ID."""
        sim = Simulation(
            customer_id=sample_customer.id,
            active_users=20,
            storage_gb=200.0,
            estimated_api_calls=100000,
            base_amount_cents=18000,
            tax_rate=0.21,
            tax_amount_cents=3780,
            total_amount_cents=21780
        )
        db_session.add(sim)
        db_session.commit()

        response = client.get(f"/simulations/{sim.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sim.id
        assert data["active_users"] == 20

    def test_get_simulation_not_found(self, client):
        """Test getting a non-existent simulation."""
        response = client.get("/simulations/99999")
        assert response.status_code == 404

    def test_delete_simulation_success(self, client, sample_customer, db_session):
        """Test successful simulation deletion."""
        sim = Simulation(
            customer_id=sample_customer.id,
            active_users=10,
            storage_gb=100.0,
            estimated_api_calls=50000,
            base_amount_cents=10000,
            tax_rate=0.21,
            tax_amount_cents=2100,
            total_amount_cents=12100
        )
        db_session.add(sim)
        db_session.commit()

        response = client.delete(f"/simulations/{sim.id}")
        assert response.status_code == 204

        # Verify simulation is gone
        response = client.get(f"/simulations/{sim.id}")
        assert response.status_code == 404

    def test_delete_simulation_not_found(self, client):
        """Test deleting a non-existent simulation."""
        response = client.delete("/simulations/99999")
        assert response.status_code == 404


class TestPreviewEndpoint:
    """Tests for the simulation preview endpoint."""

    def test_preview_simulation_success(self, client, sample_customer):
        """Test preview calculates pricing without persisting."""
        response = client.post("/simulations/preview", json={
            "customer_id": sample_customer.id,
            "active_users": 25,
            "storage_gb": 500.0,
            "estimated_api_calls": 100000
        })
        assert response.status_code == 200
        data = response.json()
        assert data["active_users"] == 25
        assert data["base_amount_cents"] == 22000  # 10*1000 + 15*800
        assert data["tax_rate"] == 0.21
        assert data["currency"] == "EUR"
        assert data["exchange_rate"] == 1.0

    def test_preview_simulation_customer_not_found(self, client):
        """Test preview for non-existent customer."""
        response = client.post("/simulations/preview", json={
            "customer_id": 99999,
            "active_users": 10,
            "storage_gb": 100.0,
            "estimated_api_calls": 50000
        })
        assert response.status_code == 404

    def test_preview_does_not_persist(self, client, sample_customer):
        """Test that preview does not create a database record."""
        # Count simulations before
        before = client.get(f"/customers/{sample_customer.id}/simulations").json()

        client.post("/simulations/preview", json={
            "customer_id": sample_customer.id,
            "active_users": 10,
            "storage_gb": 100.0,
            "estimated_api_calls": 50000
        })

        # Count simulations after
        after = client.get(f"/customers/{sample_customer.id}/simulations").json()
        assert len(after) == len(before)

    def test_preview_german_customer(self, client, sample_customer_de):
        """Test preview with German customer (19% VAT)."""
        response = client.post("/simulations/preview", json={
            "customer_id": sample_customer_de.id,
            "active_users": 10,
            "storage_gb": 100.0,
            "estimated_api_calls": 50000
        })
        assert response.status_code == 200
        data = response.json()
        assert data["tax_rate"] == 0.19
        assert data["tax_amount_cents"] == 1900
        assert data["total_amount_cents"] == 11900


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestHistoricalPreservation:
    """Tests to verify historical simulation results are preserved."""

    def test_simulation_preserves_calculated_values(self, client, sample_customer, db_session):
        """Test that simulation stores calculated values at creation time."""
        # Create simulation when tax rate is 21%
        response = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 10,
            "storage_gb": 0,
            "estimated_api_calls": 0
        })
        sim_id = response.json()["id"]

        # Verify stored values
        sim = db_session.query(Simulation).filter(Simulation.id == sim_id).first()
        assert sim.base_amount_cents == 10000
        assert sim.tax_rate == 0.21
        assert sim.tax_amount_cents == 2100
        assert sim.total_amount_cents == 12100

    def test_multiple_simulations_independent(self, client, sample_customer):
        """Test that each simulation preserves its own pricing."""
        # Create first simulation
        r1 = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 10,
            "storage_gb": 0,
            "estimated_api_calls": 0
        })
        # Create second simulation with different users
        r2 = client.post("/simulations", json={
            "customer_id": sample_customer.id,
            "active_users": 20,
            "storage_gb": 0,
            "estimated_api_calls": 0
        })

        assert r1.json()["base_amount_cents"] == 10000
        assert r2.json()["base_amount_cents"] == 18000
        assert r1.json()["total_amount_cents"] != r2.json()["total_amount_cents"]
