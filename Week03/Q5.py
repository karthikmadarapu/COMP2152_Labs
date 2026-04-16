contacts = {"Alice":"555-1234",
            "Bob":"555-5678",
            "Charlie": "555-9999"
}
print(f"Alice's Number: {contacts["Alice"]}")
contacts["Diana"] = "555-7584"
print(f"Contacts After adding Diana: {contacts}")
contacts["Bob"] = "555-0000"
print(f"Contacts After updating Bob: {contacts}")
del contacts["Charlie"]
print(f"Contacts After Deleting Charlie: {contacts}")
print(f"All names {contacts.keys()}")
print(f"All numbers {contacts.values()}")
print(f"Total contats {len(contacts)}")