from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from pets.models import Pet

from .models import AdoptionRequest

FORM = {
    "address": "House 1, Road 2, Dhaka", "phone": "+8801700000000",
    "reason": "I love dogs", "previous_pet_experience": "True", "message": "",
}


class BusinessRuleTests(TestCase):
    def setUp(self):
        self.rahim = User.objects.create_user("rahim", password="pw12345!x")
        self.karim = User.objects.create_user("karim", password="pw12345!x")
        self.max = Pet.objects.create(name="Max", animal_type="Dog", breed="Golden Retriever",
                                      age=2, gender="Male", location="Dhaka", description="Friendly")

    def apply(self, user, pet=None):
        self.client.force_login(user)
        return self.client.post(reverse("adoptions:apply", args=[(pet or self.max).pk]), FORM)

    def test_rule1_adopted_pet_cannot_be_applied_for(self):
        self.max.status = Pet.Status.ADOPTED
        self.max.save()
        self.apply(self.rahim)
        self.assertEqual(AdoptionRequest.objects.count(), 0)
        detail = self.client.get(reverse("pets:detail", args=[self.max.pk]))
        self.assertContains(detail, "already been adopted")
        self.assertNotContains(detail, "Apply for Adoption")

    def test_rule2_no_duplicate_pending_request(self):
        self.apply(self.rahim)
        self.apply(self.rahim)
        self.assertEqual(AdoptionRequest.objects.filter(user=self.rahim).count(), 1)

    def test_rule3_approval_marks_pet_adopted_and_blocks_others(self):
        self.apply(self.rahim)
        self.apply(self.karim)
        req = AdoptionRequest.objects.get(user=self.rahim)
        req.status = AdoptionRequest.Status.APPROVED
        req.save()
        self.max.refresh_from_db()
        self.assertEqual(self.max.status, Pet.Status.ADOPTED)
        other = AdoptionRequest.objects.get(user=self.karim)
        self.assertEqual(other.status, AdoptionRequest.Status.REJECTED)
        # and nobody can apply any more
        self.apply(User.objects.create_user("new", password="pw12345!x"))
        self.assertEqual(AdoptionRequest.objects.filter(pet=self.max).count(), 2)

    def test_login_required_for_apply(self):
        r = self.client.get(reverse("adoptions:apply", args=[self.max.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertIn("login", r["Location"])


class ApiTests(TestCase):
    def setUp(self):
        self.rahim = User.objects.create_user("rahim", password="pw12345!x")
        self.karim = User.objects.create_user("karim", password="pw12345!x")
        self.admin = User.objects.create_superuser("admin", password="pw12345!x")
        self.max = Pet.objects.create(name="Max", animal_type="Dog", breed="Golden Retriever",
                                      age=2, gender="Male", location="Dhaka", description="Friendly")
        Pet.objects.create(name="Luna", animal_type="Cat", breed="Persian",
                           age=1, gender="Female", location="Sylhet", description="Calm")
        self.api = APIClient()

    def payload(self):
        return {"pet": self.max.pk, "phone": "01700000000", "address": "Dhaka",
                "reason": "Love", "previous_pet_experience": True}

    def test_pet_list_search_filter_public(self):
        self.assertEqual(self.api.get("/api/pets/").data["count"], 2)
        self.assertEqual(self.api.get("/api/pets/?search=golden").data["count"], 1)
        self.assertEqual(self.api.get("/api/pets/?animal_type=Cat").data["count"], 1)
        self.assertEqual(self.api.get("/api/pets/?gender=Male").data["results"][0]["name"], "Max")

    def test_only_admin_can_write_pets(self):
        body = {"name": "Rex", "animal_type": "Dog", "age": 1, "gender": "Male",
                "location": "Dhaka", "description": "x"}
        self.assertEqual(self.api.post("/api/pets/", body).status_code, 401)
        self.api.force_authenticate(self.rahim)
        self.assertEqual(self.api.post("/api/pets/", body).status_code, 403)
        self.api.force_authenticate(self.admin)
        self.assertEqual(self.api.post("/api/pets/", body).status_code, 201)

    def test_users_only_see_own_requests(self):
        self.api.force_authenticate(self.rahim)
        rid = self.api.post("/api/adoptions/", self.payload(), format="json").data["id"]
        self.assertEqual(self.api.get("/api/adoptions/").data["count"], 1)
        self.api.force_authenticate(self.karim)
        self.assertEqual(self.api.get("/api/adoptions/").data["count"], 0)
        self.assertEqual(self.api.get(f"/api/adoptions/{rid}/").status_code, 404)

    def test_api_enforces_rules_and_blocks_status_tampering(self):
        self.api.force_authenticate(self.rahim)
        r = self.api.post("/api/adoptions/", {**self.payload(), "status": "Approved"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["status"], "Pending")
        self.assertEqual(self.api.post("/api/adoptions/", self.payload(), format="json").status_code, 400)
        self.max.status = "Adopted"; self.max.save()
        self.api.force_authenticate(self.karim)
        self.assertEqual(self.api.post("/api/adoptions/", self.payload(), format="json").status_code, 400)

    def test_token_auth(self):
        res = self.api.post("/api/token/", {"username": "rahim", "password": "pw12345!x"})
        self.assertEqual(res.status_code, 200)
        c = APIClient(); c.credentials(HTTP_AUTHORIZATION="Token " + res.data["token"])
        self.assertEqual(c.get("/api/adoptions/").status_code, 200)
        self.assertEqual(APIClient().get("/api/adoptions/").status_code, 401)
