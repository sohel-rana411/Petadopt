from django.core.management.base import BaseCommand

from pets.models import Pet

SAMPLES = [
    ("Max", "Dog", "Golden Retriever", 2, "Male", "Dhaka", "Max is friendly and playful, great with kids."),
    ("Luna", "Cat", "Persian", 1, "Female", "Chattogram", "Luna is calm, fluffy and loves laps."),
    ("Coco", "Rabbit", "Holland Lop", 1, "Female", "Dhaka", "Coco is gentle and enjoys fresh carrots."),
    ("Rocky", "Dog", "Labrador", 3, "Male", "Sylhet", "Rocky is energetic and loves long walks."),
    ("Mimi", "Cat", "Siamese", 2, "Female", "Dhaka", "Mimi is talkative and very affectionate."),
    ("Kiwi", "Bird", "Cockatiel", 1, "Male", "Khulna", "Kiwi whistles tunes and likes company."),
    ("Bruno", "Dog", "German Shepherd", 4, "Male", "Dhaka", "Bruno is loyal, trained and protective."),
    ("Snowy", "Cat", "Domestic Shorthair", 0, "Female", "Rajshahi", "Snowy is a playful kitten."),
    ("Buddy", "Dog", "Beagle", 5, "Male", "Dhaka", "Buddy is a sweet senior with lots of love left."),
    ("Pip", "Other", "Guinea Pig", 1, "Male", "Dhaka", "Pip squeaks happily at snack time."),
]


class Command(BaseCommand):
    help = "Create sample pets for demo purposes."

    def handle(self, *args, **options):
        if Pet.objects.exists():
            self.stdout.write("Pets already exist; skipping.")
            return
        for name, kind, breed, age, gender, loc, desc in SAMPLES:
            Pet.objects.create(name=name, animal_type=kind, breed=breed, age=age,
                               gender=gender, location=loc, description=desc)
        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLES)} sample pets."))
