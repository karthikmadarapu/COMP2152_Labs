monday_class = {"Alice", "Bob", "Charlie", "Lema"}
wednesday_class = {"Diana", "Mohammed", "Bob", "Justin", "Saad"}

monday_class.add("Grace")
print(f"Monday Class Students: {monday_class}")
print(f"Wednesday Class Students: {wednesday_class}")
print(f"Merged Classes: {monday_class & wednesday_class}")
print(f"Attended Either Classes : {monday_class | wednesday_class}")
print(f"Only Monday Class: {monday_class - wednesday_class}")
print(f"Only One Class: {monday_class ^ wednesday_class}")
allStudents = monday_class | wednesday_class
print("Is MONDAY subset of all students? ", monday_class <= allStudents)
